import time
import schedule
from core.database import SessionLocal
from ingestion.pipeline import IngestionPipeline

def run_etl_job():
    print("⏰ Scheduler: Starting scheduled ETL job...")
    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        
        # Run all sources
        pipeline.fetch_coinpaprika()
        pipeline.fetch_coingecko()
        
        # Process data
        pipeline.process_raw_data()
        print("✅ Scheduler: Job finished successfully.")
    except Exception as e:
        print(f"❌ Scheduler: Job failed - {e}")
    finally:
        db.close()

def start_scheduler():
    # Schedule the job to run every 1 minute (for demo purposes)
    # In production, you might change this to .hours.do(run_etl_job)
    schedule.every(1).minutes.do(run_etl_job)
    
    # Run once immediately on startup so we have data right away
    run_etl_job()

    print("🚀 ETL Scheduler is running...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_scheduler()