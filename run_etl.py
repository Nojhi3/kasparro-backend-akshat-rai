import os
from core.database import SessionLocal
from ingestion.pipeline import IngestionPipeline

def main():
    db = SessionLocal()
    pipeline = IngestionPipeline(db)
    
    try:
        print("--- Starting ETL Run ---")
        
        # 1. APIs
        pipeline.fetch_coinpaprika()
        pipeline.fetch_coingecko()
        
        # 2. CSV (Check if file exists first)
        csv_file = "historical_prices.csv"
        if os.path.exists(csv_file):
            pipeline.fetch_csv_data(csv_file)
        else:
            print("⚠️ No CSV file found. Skipping.")
        
        # 3. Process All
        # Note: You need to ensure process_raw_data calls both _process_api_tables AND _process_csv_tables
        # or simply put the logic in one big function as before.
        pipeline.process_raw_data()
        
        print("--- ETL Run Finished Successfully ---")
        
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()