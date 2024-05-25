"""Script to create an admin user"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole

def create_admin(email: str = "noura@example.com", password: str = "admin123"):
    """Create an admin user"""
    db: Session = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User with email {email} already exists")
            return
        
        # Create admin user
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"Admin user created: {email}")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default="noura@example.com")
    parser.add_argument("--password", default="admin123")
    args = parser.parse_args()
    create_admin(args.email, args.password)
