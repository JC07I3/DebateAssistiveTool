# Data/database.py
import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from dotenv import load_dotenv
from .models import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///data.db"


# 使用 Streamlit 快取資料庫引擎，避免多執行緒下反覆建立連線
@st.cache_resource
def get_engine():
    engine = create_engine(DATABASE_URL, echo=False)
    # 確保所有結構被創建 (新增多對多表格)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session_maker():
    engine = get_engine()
    return sessionmaker(bind=engine, autocommit=False)

@contextmanager
def db_session():
    """提供 Session 的 Context Manager，具備防呆與自動 Rollback 功能"""
    Session = get_session_maker()
    db = Session()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
