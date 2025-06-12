from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv
from .models.base import Base  # Import Base from models.base

# Load environment variables
load_dotenv()

# Get the directory of the current file
BASE_DIR = Path(__file__).resolve().parent.parent

# Create the database directory if it doesn't exist
db_dir = BASE_DIR / "data"
db_dir.mkdir(exist_ok=True)

# Database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_dir}/app.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database."""
    # Import all models here to ensure they are registered with Base
    from .models import Base, Server, SecurityEvent, AttackLog, Alert, User, TrafficStats
    
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
