import argparse
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.document import Document
from backend.app.services.auth import hash_password


def create_or_update_admin(email: str, password: str, name: str = "GCET Administrator"):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if user:
            print(f"User with email '{email}' already exists.")
            print(f"Updating user role to 'admin' and resetting password...")
            user.role = "admin"
            user.password_hash = hash_password(password)
            if name:
                user.name = name
            db.commit()
            print(f"SUCCESS: Account '{email}' updated to Administrator role.")
        else:
            print(f"Creating new Administrator account for '{email}'...")
            admin_user = User(
                name=name,
                email=email,
                password_hash=hash_password(password),
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            print(f"SUCCESS: Administrator account '{email}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to create/update administrator account: {e}")
        sys.exit(1)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Securely create or update a GCET Administrator account.")
    parser.add_argument("--email", type=str, help="Admin email address")
    parser.add_argument("--password", type=str, help="Admin password")
    parser.add_argument("--name", type=str, default="GCET Administrator", help="Admin full name")

    args = parser.parse_args()

    email = args.email
    password = args.password
    name = args.name

    if not email:
        email = input("Enter Admin Email: ").strip()
    if not password:
        import getpass
        password = getpass.getpass("Enter Admin Password: ").strip()

    if not email or not password:
        print("ERROR: Email and password are required.")
        sys.exit(1)

    create_or_update_admin(email=email, password=password, name=name)


if __name__ == "__main__":
    main()
