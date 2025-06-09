from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"  # You can replace it with PostgreSQL, MySQL, etc.

# Create engine to connect to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create a session local to manage connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for all your models
Base = declarative_base()

# Import models to ensure they are registered with SQLAlchemy's Base
from . import models

# Dependency for getting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Fixing the typo here (removed 'a' at the end)
        
# Create all tables in the database (for SQLite, Postgres, etc.)
Base.metadata.create_all(bind=engine)
