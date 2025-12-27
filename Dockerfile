# Use Python 3.11 Slim (Lightweight & Fast)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 --retries 10 -r requirements.txt


# Copy the rest of the code
COPY . .

# Make sure the start script is executable
RUN chmod +x start.sh

# Expose the API port
EXPOSE 8000

# Run the start script
CMD ["./start.sh"]