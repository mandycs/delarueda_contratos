import argparse
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import SessionLocal

def main():
    parser = argparse.ArgumentParser(description="Create a new user.")
    parser.add_argument("--username", required=True, help="The username for the new user.")
    parser.add_argument("--password", required=True, help="The password for the new user.")
    parser.add_argument("--email", help="The email for the new user.")
    parser.add_argument("--full-name", help="The full name of the new user.")

    args = parser.parse_args()

    db: Session = SessionLocal()

    db_user = crud.get_user_by_username(db, username=args.username)
    if db_user:
        print(f"Username '{args.username}' already registered.")
        return

    user_in = schemas.UserCreate(  # <--- aquí estaba el problema
        username=args.username,
        password=args.password,
        email=args.email,
        full_name=args.full_name
    )

    user = crud.create_user(db=db, user=user_in)
    print(f"User '{user.username}' created successfully.")

if __name__ == "__main__":
    main()
