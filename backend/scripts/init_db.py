"""Initialize database"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models import *  # Import all models

def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized")

if __name__ == "__main__":
    init_db()
