from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory of the current file
BASE_DIR = Path(__file__).resolve().parent.parent

# Create the database directory if it doesn't exist
db_dir = BASE_DIR / "data"
db_dir.mkdir(exist_ok=True)

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_dir}/app.db")

# Create engine with optimized pool settings
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory with optimized settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with all models."""
    try:
        # Import all models here to ensure they are registered with SQLAlchemy
        from .models import Server, ServerHealth, ServerStats, SecurityEvent, AttackLog, TrafficStats
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
