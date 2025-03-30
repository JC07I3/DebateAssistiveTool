from sqlalchemy import Integer, String, Column, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import scoped_session
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

eng = None
session = None

def get_engine():
    global eng
    if eng is None:
        eng = create_engine(DATABASE_URL, echo=True)
    return eng

def get_session():
    global session
    if session is not None:
        return session
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    session = scoped_session(sessionmaker(bind=engine, autocommit=False))
    return session 

Session = get_session()

def add_contest(name):
    db = Session()
    new_contest = Contest(name=name)
    db.add(new_contest)
    db.commit()
    db.close()
    get_contests.cache_clear()

def remove_contest(name):
    db = Session()
    qry = db.query(Contest).filter(Contest.name == str(name)).first()
    if qry:
        db.delete(qry)
    db.commit()
    db.close()
    get_contests.cache_clear()

@lru_cache
def get_contests():
    db = Session()
    qry = db.query(Contest)
    ret = [i.name for i in qry]
    db.close()
    return list(reversed(ret))

if __name__ == "__main__":
    remove_contest("123")