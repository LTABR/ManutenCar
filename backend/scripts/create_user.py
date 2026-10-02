import argparse
import sys
from pathlib import Path
from uuid import uuid4

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import Base, SessionLocal, engine
from app.models import User
from app.security import hash_password


parser = argparse.ArgumentParser(description="Create a ManutenCar user")
parser.add_argument("email")
parser.add_argument("password")
args = parser.parse_args()

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    db.add(User(id=str(uuid4()), email=args.email.strip().lower(), password_hash=hash_password(args.password)))
    db.commit()
print(f"Created user {args.email.strip().lower()}")
