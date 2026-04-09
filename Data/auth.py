import bcrypt
from .models import User
from .database import db_session

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username: str, password: str) -> bool:
    with db_session() as db:
        if db.query(User).filter(User.username == username).first():
            return False  # Username exists
        
        hashed = hash_password(password)
        new_user = User(username=username, password_hash=hashed)
        db.add(new_user)
        return True

def verify_user_login(username: str, password: str):
    with db_session() as db:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return {"id": user.id, "username": user.username}
    return None

def get_user_by_username(username: str):
    with db_session() as db:
        user = db.query(User).filter(User.username == username).first()
        if user:
            return {"id": user.id, "username": user.username}
    return None
