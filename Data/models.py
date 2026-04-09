# Data/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

# 多對多關聯表：Debate <-> Tag
debate_tag_mapping = Table(
    'debate_tag_mapping',
    Base.metadata,
    Column('debate_id', Integer, ForeignKey('debates.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

# 多對多關聯表：User <-> Contest (權限管理)
contest_user_mapping = Table(
    'contest_user_mapping',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('contest_id', Integer, ForeignKey('contests.id', ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    
    contests = relationship("Contest", secondary=contest_user_mapping, back_populates="users")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contest = Column(String)
    
    # 關聯回 Debate
    debates = relationship("Debate", secondary=debate_tag_mapping, back_populates="tags")

class Debate(Base):
    __tablename__ = "debates"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    link = Column(String) 
    
    # 舊的 tags = Column(String) 建議在資料庫遷移後刪除，此處直接依賴 ORM 的 M2M
    # 如果要保留相容可以保留此欄位名但這會與 relationship 名稱衝突，故不宣告舊的 tags 欄位，
    # 而把 relationship 直接命名為 tags。
    content = Column(Text)
    side = Column(String)
    contest = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # 關聯至 Tag
    tags = relationship("Tag", secondary=debate_tag_mapping, back_populates="debates", lazy='subquery')
    # 關聯至 History
    history = relationship("DebateHistory", back_populates="debate", cascade="all, delete-orphan", order_by="desc(DebateHistory.changed_at)")

class DebateHistory(Base):
    __tablename__ = "debate_history"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    debate_id = Column(Integer, ForeignKey('debates.id', ondelete="CASCADE"), index=True)
    editor_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    title = Column(String)
    content = Column(Text)
    side = Column(String)
    changed_at = Column(DateTime, default=datetime.datetime.now)
    
    debate = relationship("Debate", back_populates="history")
    editor = relationship("User")

class Contest(Base):
    __tablename__ = "contests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    
    # 關聯至 User
    users = relationship("User", secondary=contest_user_mapping, back_populates="contests")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    content = Column(Text)
    contest = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

class Script(Base):
    __tablename__ = "scripts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    side = Column(String) 
    content = Column(Text)
    contest = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
