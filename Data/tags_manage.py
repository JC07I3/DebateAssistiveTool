from sqlalchemy import Integer, String, Column, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import scoped_session
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contest = Column(String)

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

def add_tag(name, contest):
    db = Session()
    new_tag = Tag(name=str(name), contest=str(contest))
    db.add(new_tag)
    db.commit()
    db.close()
    get_tags.cache_clear()

def remove_tag(name, contest):
    db = Session()
    qry = db.query(Tag).filter(Tag.name == str(name) and Tag.contest == str(contest)).first()
    if qry:
        db.delete(qry)
    db.commit()
    db.close()
    get_tags.cache_clear()

@lru_cache(maxsize=128)
def get_tags(contest):
    db = Session()
    qry = db.query(Tag).filter(Tag.contest == str(contest)).all()
    ret = []
    if qry:
        ret = [i.name for i in qry]
    db.close()
    return list(reversed(ret))

