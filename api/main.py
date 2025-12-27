from fastapi import FastAPI
from api.routes import health, data

app = FastAPI(
    title="Kasparro ETL API",
    description="Backend system for ingesting and exposing data.",
    version="1.0.0"
)

# Include the routers
app.include_router(health.router)
app.include_router(data.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)