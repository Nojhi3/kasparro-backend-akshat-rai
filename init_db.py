from core.database import engine, Base
from core.models import RawAPIData, RawCSVData, UnifiedData, ETLCheckpoint

# This command looks at all classes inheriting from Base and creates tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")