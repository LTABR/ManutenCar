from db import engine
from sqlalchemy import text

def executar_limpeza():
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users WHERE email LIKE 'deleted_%'"))
        conn.commit()

if __name__ == "__main__":
    executar_limpeza()
