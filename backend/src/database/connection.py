import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "nytp.db")

def get_engine(db_path: str = DB_PATH) -> Engine:
    return create_engine(f"sqlite:///{db_path}", echo=False)

def get_mysql_engine(user: str = "root", password: str = "", host: str = "localhost", db: str = "nytp") -> Engine:
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db}", echo=False)

def test_connection(engine: Engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
