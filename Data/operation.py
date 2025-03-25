from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, or_
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import scoped_session
import datetime
import pandas as pd
from functools import lru_cache

DATABASE_URL = "sqlite:///data.db"

Base = declarative_base()

class Debate(Base):
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    link = Column(String) 
    tags = Column(String) 
    content = Column(Text)
    side = Column(String)
    contest = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now().date())

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

def add_data(title, link, tags, content, side, contest):
    db = Session()
    new_debate = Debate(title=title, link=link, tags=tags, content=content, side=side, contest=contest)
    db.add(new_debate)
    db.commit()
    db.close()
    search_data.cache_clear()

@lru_cache(maxsize=128)
def search_data(title=None, tags=None, content=None, side=None, contest=None):
    db = Session()
    query = db.query(Debate)

    if title:
        query = query.filter(or_(Debate.title.contains(title)))
    if tags:
        query = query.filter(Debate.tags.contains(tags))
    if content:
        query = query.filter(or_(Debate.content.contains(content)))
    if side:
        query = query.filter(Debate.side == side)
    if contest:
        query = query.filter(Debate.contest == contest)

    result = pd.read_sql_query(query.statement, db.bind)
    db.close()
    return result

def update_data(debate_id, title=None, link=None, tags=None, content=None, side=None, contest=None):
    db = Session()
    debate = db.query(Debate).filter(Debate.id == int(debate_id)).first()
    if debate:
        if title:
            debate.title = title
        if link:
            debate.link = link
        if tags:
            debate.tags = tags
        if content:
            debate.content = content
        if side:
            debate.side = side
        if contest:
            debate.contest = contest
        db.commit()
    db.close()
    search_data.cache_clear()

def delete_data(debate_id):
    db = Session()
    data_tmp = db.query(Debate).filter(Debate.id == int(debate_id)).first()
    if data_tmp:
        db.delete(data_tmp)
    db.commit()
    db.close()
    search_data.cache_clear()

# 測試功能
if __name__ == "__main__":
    pass