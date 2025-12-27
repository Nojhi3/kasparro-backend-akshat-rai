import csv
import uuid
from datetime import datetime, timedelta

def generate_csv():
    filename = "historical_prices.csv"
    
    # Define our CSV headers
    headers = ["ticker", "close_price", "trade_date", "trade_id"]
    
    # Create dummy data (e.g., Ethereum prices from last week)
    data = [
        ["ETH", 2950.50, (datetime.now() - timedelta(days=1)).isoformat(), str(uuid.uuid4())],
        ["ETH", 2900.25, (datetime.now() - timedelta(days=2)).isoformat(), str(uuid.uuid4())],
        ["BTC", 58000.00, (datetime.now() - timedelta(days=1)).isoformat(), str(uuid.uuid4())],
        ["SOL", 145.20, (datetime.now() - timedelta(days=1)).isoformat(), str(uuid.uuid4())],
    ]

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
        
    print(f"Created {filename} with {len(data)} rows.")

if __name__ == "__main__":
    generate_csv()