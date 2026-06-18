from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Путь к файлу базы данных, который создастся сам
DATABASE_URL = "sqlite:///./jobs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Настройка подключения для каждого запроса к сайту
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
