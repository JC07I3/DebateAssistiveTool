from functools import lru_cache
from .models import Tag
from .database import db_session

def add_tag(name, contest):
    with db_session() as db:
        new_tag = Tag(name=str(name), contest=str(contest))
        db.add(new_tag)
    get_tags.cache_clear()

def remove_tag(name, contest):
    with db_session() as db:
        tag = db.query(Tag).filter(Tag.name == str(name), Tag.contest == str(contest)).first()
        if tag:
            db.delete(tag)
    get_tags.cache_clear()

@lru_cache(maxsize=128)
def get_tags(contest):
    with db_session() as db:
        tags = db.query(Tag).filter(Tag.contest == str(contest)).all()
        ret = [t.name for t in tags]
    return list(reversed(ret))
