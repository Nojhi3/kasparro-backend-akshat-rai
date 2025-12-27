#!/bin/bash

# 1. Start the ETL Scheduler in the background (&)
python -m services.scheduler &

# 2. Start the API Server in the foreground
# This keeps the container alive
uvicorn api.main:app --host 0.0.0.0 --port 8000