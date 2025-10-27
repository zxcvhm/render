import sqlite3
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os 
from pathlib import Path

# 환경변수 설정
ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(ENV_PATH)

# render.yaml에 직접 지정한 환경변수 가져오기 
DB_URL = os.getenv("DB_URL")

# 엔진
engine = create_engine(DB_URL)

# 세션 
SessionLocal = sessionmaker(autocommit=False,  # 확정을 자동으로 주지 않겠다 
                            autoflush=False,   # 새로고침을 자동으로 하지 않겠다 
                            bind=engine)       # 어떤 데이터베이스랑 연결시켜서 세션을 만들건지 지정


# Base 모델
Base = declarative_base() # 이 클래스는 데이터 베이스 테이블과 파이썬의 클래스와 연결해주는 역할을 한다 


# Base 모델에 등록된 모델 클래스를 생성해주는 create_table 함수 
def create_tables():
    """ORM 모델(파이썬 클래스)를 
    데이터 베이스 테이블로 생성하는 함수"""
    
    # engine과 연결된 데이터베이스에 데이터 베이스 테이블 생성
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try: 
        yield db    # yield가 포함되어 있는 함수는 generator 
    finally: 
        db.close()
        

