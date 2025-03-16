from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, or_
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import pandas as pd

DATABASE_URL = "sqlite:///C:\Users\chens\OneDrive\桌面\專案\DebateAssistiveTool\data.db"
engine = create_engine(DATABASE_URL, echo=True)

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
    created_at = Column(DateTime, default=datetime.datetime.now)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine, autocommit=False)

def add_data(title, link, tags, content, side, contest):
    db = SessionLocal()
    new_debate = Debate(title=title, link=link, tags=tags, content=content, side=side, contest=contest)
    db.add(new_debate)
    db.commit()
    db.close()

def search_data(title=None, tags=None, content=None, side=None, contest=None):
    db = SessionLocal()
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
    db = SessionLocal()
    debate = db.query(Debate).filter(Debate.id == debate_id).first()
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

def delete_data(debate_id):
    db = SessionLocal()
    debate = db.query(Debate).filter(Debate.id == debate_id).first()
    if debate:
        db.delete(debate)
        db.commit()
    db.close()

# 測試功能
if __name__ == "__main__":
    pass