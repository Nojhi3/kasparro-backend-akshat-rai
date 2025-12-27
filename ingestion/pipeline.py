import os
import requests
import json
import pandas as pd # <--- Added pandas
from datetime import datetime
from sqlalchemy.orm import Session
from core.models import RawAPIData, RawCSVData, UnifiedData
from schemas.etl_schema import UnifiedRow

class IngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_coinpaprika(self):
        # We use the 'tickers' endpoint to get a list of all coins and prices
        url = "https://api.coinpaprika.com/v1/tickers"
        api_key = os.getenv("COINPAPRIKA_API_KEY") # Ensure this is in your .env
        
        print("Fetching CoinPaprika data...")
        try:
            # CoinPaprika usually expects the ID in the header or query param.
            # Free tier often works without it, but we add it if present.
            headers = {}
            if api_key:
                headers = {"Authorization": api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            # Limiting to first 50 to avoid hitting rate limits or massive DB writes during dev
            data = data[:50] 
            
            # Store Raw Data
            raw_record = RawAPIData(
                source_name="coinpaprika",
                payload=data, 
                processed=False
            )
            self.db.add(raw_record)
            self.db.commit()
            print(f"✅ Saved {len(data)} records from CoinPaprika.")
            
        except Exception as e:
            print(f"❌ Error fetching CoinPaprika: {e}")

    # --- SOURCE 2: CoinGecko (Public) ---
    def fetch_coingecko(self):
        # We use the 'markets' endpoint to get price + market cap
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1
        }
        
        print("Fetching CoinGecko data...")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Store Raw Data
            raw_record = RawAPIData(
                source_name="coingecko",
                payload=data,
                processed=False
            )
            self.db.add(raw_record)
            self.db.commit()
            print(f"✅ Saved {len(data)} records from CoinGecko.")
            
        except Exception as e:
            print(f"❌ Error fetching CoinGecko: {e}")

    # --- SOURCE 3: CSV File (Local File System) ---
    def fetch_csv_data(self, file_path: str):
        print(f"Reading CSV from {file_path}...")
        try:
            # Pandas makes it easy to read CSVs and convert to JSON
            df = pd.read_csv(file_path)
            
            records = df.to_dict(orient="records") # Converts to list of dicts
            
            # Store EACH row as a raw record (or you could store the whole file as one blob)
            # Storing row-by-row is better for tracking individual processing success/failure
            new_records = []
            for row in records:
                new_records.append(RawCSVData(
                    filename=file_path,
                    row_data=row, # Stores {"ticker": "ETH", "price": ...} as JSONB
                    processed=False
                ))
            
            self.db.add_all(new_records)
            self.db.commit()
            print(f"✅ Saved {len(new_records)} CSV rows to Postgres.")
            
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")

    # --- TRANSFORMATION LOGIC ---
    def process_raw_data(self):
        """
        Reads unprocessed raw rows (API + CSV), detects source, and normalizes.
        """
        # 1. Process API Data (Existing logic)
        self._process_api_tables()
        
        # 2. Process CSV Data (New logic)
        self._process_csv_tables()

    def _process_api_tables(self):
        """
        Reads unprocessed raw rows, detects the source, and normalizes them.
        """
        # Get all raw rows that haven't been processed yet
        raw_rows = self.db.query(RawAPIData).filter(RawAPIData.processed == False).all()
        
        if not raw_rows:
            print("No new raw data to process.")
            return

        for row in raw_rows:
            payload = row.payload # This is the list of coins
            now = datetime.utcnow() # Timestamp for when we processed this

            print(f"Processing batch from: {row.source_name}...")

            for item in payload:
                try:
                    clean_data = None
                    
                    # --- MAPPING LOGIC FOR COINPAPRIKA ---
                    if row.source_name == "coinpaprika":
                        # Structure: {'id': 'btc-bitcoin', 'name': 'Bitcoin', 'quotes': {'USD': {'price': 20000}}}
                        
                        # Safely access nested dictionary for price
                        quotes = item.get("quotes", {})
                        usd_quote = quotes.get("USD", {})
                        price = usd_quote.get("price", 0)

                        clean_data = UnifiedRow(
                            entity_name=item.get("name", "Unknown"),
                            value=float(price),
                            event_timestamp=now, 
                            source="coinpaprika",
                            original_id=item.get("id")
                        )

                    # --- MAPPING LOGIC FOR COINGECKO ---
                    elif row.source_name == "coingecko":
                        # Structure: {'id': 'bitcoin', 'name': 'Bitcoin', 'current_price': 20000}
                        
                        clean_data = UnifiedRow(
                            entity_name=item.get("name", "Unknown"),
                            value=float(item.get("current_price", 0)),
                            event_timestamp=now,
                            source="coingecko",
                            original_id=item.get("id")
                        )

                    # --- LOAD INTO UNIFIED TABLE ---
                    if clean_data:
                        unified_db_row = UnifiedData(
                            entity_name=clean_data.entity_name,
                            value=clean_data.value,
                            event_timestamp=clean_data.event_timestamp,
                            source=clean_data.source,
                            original_id=clean_data.original_id
                        )
                        self.db.add(unified_db_row)

                except Exception as e:
                    # Log error but don't stop the whole pipeline
                    print(f"⚠️ Skipping bad row in {row.source_name}: {e}")

            # Mark batch as processed so we don't do it again
            row.processed = True
            self.db.commit()
        
        print(f"✅ Transformation complete. Processed {len(raw_rows)} batches.")

    def _process_csv_tables(self):
        raw_rows = self.db.query(RawCSVData).filter(RawCSVData.processed == False).all()
        
        if not raw_rows:
            return

        print(f"Processing {len(raw_rows)} CSV rows...")
        
        for row in raw_rows:
            try:
                data = row.row_data # This is a dictionary
                
                # CSV Structure: ticker, close_price, trade_date, trade_id
                clean_data = UnifiedRow(
                    entity_name=data.get("ticker"),
                    value=float(data.get("close_price")),
                    event_timestamp=datetime.fromisoformat(data.get("trade_date")),
                    source="historical_csv",
                    original_id=data.get("trade_id")
                )
                
                # Load to Unified
                self.db.add(UnifiedData(
                    entity_name=clean_data.entity_name,
                    value=clean_data.value,
                    event_timestamp=clean_data.event_timestamp,
                    source=clean_data.source,
                    original_id=clean_data.original_id
                ))
                
                row.processed = True
                
            except Exception as e:
                print(f"⚠️ Skipping bad CSV row {row.id}: {e}")
        
        self.db.commit()
        print(f"✅ CSV Processing complete.")