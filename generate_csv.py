import pandas as pd
import yfinance as yf
import uuid

def generate_real_csv():
    print("Fetching REAL data for multiple coins from Yahoo Finance...")
    
    # 1. Define the list of coins you want
    # Yahoo Finance uses these ticker symbols
    coins = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD"]
    
    all_data = []

    for coin in coins:
        print(f"Downloading {coin}...")
        try:
            # Fetch data for Jan 2024
            df = yf.download(coin, start="2024-01-01", end="2024-07-01", progress=False)
            
            if df.empty:
                continue

            df.reset_index(inplace=True)
            
            # Create a clean temporary DataFrame
            temp_df = pd.DataFrame()
            
            # Set Date
            temp_df['trade_date'] = df['Date'].apply(lambda x: x.isoformat())
            
            # Set Ticker (Remove '-USD' so it looks clean in DB like 'BTC', 'ETH')
            clean_ticker = coin.split('-')[0]
            temp_df['ticker'] = clean_ticker
            
            # Set Price (Handle MultiIndex safety)
            if isinstance(df['Close'], pd.DataFrame):
                temp_df['close_price'] = df['Close'].iloc[:, 0]
            else:
                temp_df['close_price'] = df['Close']
            
            # Generate IDs
            temp_df['trade_id'] = [str(uuid.uuid4()) for _ in range(len(temp_df))]
            
            all_data.append(temp_df)
            
        except Exception as e:
            print(f"⚠️ Skipped {coin} due to error: {e}")

    # 2. Combine all coins into one big table
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        # 3. Clean up NaNs
        final_df.dropna(inplace=True)
        
        # 4. Save
        filename = "historical_prices.csv"
        final_df.to_csv(filename, index=False)
        print(f"✅ Success! Created {filename} with {len(final_df)} rows for {len(coins)} coins.")
    else:
        print("❌ No data fetched.")

if __name__ == "__main__":
    generate_real_csv()