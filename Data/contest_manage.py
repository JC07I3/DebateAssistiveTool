from sqlalchemy import Integer, String, Column, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///data.db"
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)

def add_contest(name):
    db = SessionLocal()
    new_contest = Contest(name=name)
    db.add(new_contest)
    db.commit()
    db.close()

def remove_contest(name):
    db = SessionLocal()
    qry = db.query(Contest).filter(Contest.name == name).first()
    db.delete(qry)
    db.commit()
    db.close()

def get_contests():
    db = SessionLocal()
    qry = db.query(Contest)
    ret = [i.name for i in qry]
    db.close()
    return list(reversed(ret))
