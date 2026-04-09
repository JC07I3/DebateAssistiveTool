from .models import Contest, User
from .database import db_session

def add_contest(name, user_id):
    with db_session() as db:
        existing = db.query(Contest).filter(Contest.name == name).first()
        if not existing:
            new_contest = Contest(name=name)
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                new_contest.users.append(user)
            db.add(new_contest)

def remove_contest(name):
    with db_session() as db:
        contest = db.query(Contest).filter(Contest.name == str(name)).first()
        if contest:
            db.delete(contest)

def get_contests(user_id):
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return list(reversed([c.name for c in user.contests]))
    return []

def share_contest(contest_name, target_username):
    with db_session() as db:
        contest = db.query(Contest).filter(Contest.name == contest_name).first()
        target_user = db.query(User).filter(User.username == target_username).first()
        if contest and target_user:
            if target_user not in contest.users:
                contest.users.append(target_user)
                return True, "成功：已加入該進協作者"
            else:
                return False, "該用戶已在協作者列表內"
        return False, "找不到該盃賽或用戶名"