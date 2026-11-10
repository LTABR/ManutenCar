from db import engine
from sqlalchemy import text

def clean_old_users():
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users WHERE email LIKE 'deleted_%'"))
        conn.commit()

if __name__ == "__main__":
    clean_old_users()
