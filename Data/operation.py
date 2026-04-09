import pandas as pd
from sqlalchemy import or_

from .models import Debate, Tag
from .database import db_session

def escape_like(string):
    """跳脫 SQL LIKE 查詢的特殊字元"""
    return string.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

def add_data(title, link, tags, content, side, contest):
    with db_session() as db:
        new_debate = Debate(title=title, link=link, content=content, side=side, contest=contest)
        if tags:
            # 傳入的是以 $ 串接的字串 (向下相容) 或是 list
            tag_names = tags.split('$') if isinstance(tags, str) else tags
            tag_names = [t for t in tag_names if t]
            if tag_names:
                matched_tags = db.query(Tag).filter(Tag.name.in_(tag_names), Tag.contest == contest).all()
                new_debate.tags = matched_tags
        db.add(new_debate)

def search_data(keyword=None, title=None, tags=None, content=None, side=None, contest=None):
    with db_session() as db:
        query = db.query(Debate)

        if keyword:
            keyword_esc = escape_like(keyword)
            query = query.filter(or_(
                Debate.title.like(f"%{keyword_esc}%", escape='\\'),
                Debate.content.like(f"%{keyword_esc}%", escape='\\')
            ))

        if title:
            # 處理萬用字元跳脫防注入
            title_esc = escape_like(title)
            query = query.filter(or_(
                Debate.title.contains(title), # 精確包含
                Debate.title.like(f"%{title_esc}%", escape='\\')
            ))
            
        if tags:
            tag_names = tags.split('$') if isinstance(tags, str) else tags
            tag_names = [t for t in tag_names if t]
            if tag_names:
                # Many-to-Many 查詢：Debate 的 tags 關聯中包含指定的 Tag 名稱
                query = query.filter(Debate.tags.any(Tag.name.in_(tag_names)))
                
        if content:
            content_esc = escape_like(content)
            query = query.filter(or_(
                Debate.content.contains(content), 
                Debate.content.like(f"%{content_esc}%", escape='\\')
            ))
            
        if side:
            query = query.filter(Debate.side == side)
            
        if contest:
            query = query.filter(Debate.contest == contest)

        results = query.all()
        
        # 為了與前端 pandas DataFrame 相容，將 ORM 結果轉換
        data = []
        for r in results:
            data.append({
                "id": r.id,
                "title": r.title,
                "link": r.link,
                "tags": "$".join([t.name for t in r.tags]), # 轉回前端需要的相容格式
                "content": r.content,
                "side": r.side,
                "contest": r.contest,
                "created_at": r.created_at
            })
            
        columns = ["id", "title", "link", "tags", "content", "side", "contest", "created_at"]
        return pd.DataFrame(data, columns=columns) if data else pd.DataFrame(columns=columns)

def update_data(debate_id, user_id, title=None, link=None, tags=None, content=None, side=None, contest=None):
    with db_session() as db:
        debate = db.query(Debate).filter(Debate.id == int(debate_id)).first()
        if debate:
            is_changed = False
            if title is not None and debate.title != title: is_changed = True
            if content is not None and debate.content != content: is_changed = True
            if side is not None and debate.side != side: is_changed = True
            
            if is_changed:
                from .models import DebateHistory
                history = DebateHistory(
                    debate_id=debate.id,
                    editor_id=user_id,
                    title=debate.title,
                    content=debate.content,
                    side=debate.side
                )
                db.add(history)

            if title is not None: debate.title = title
            if link is not None: debate.link = link
            if content is not None: debate.content = content
            if side is not None: debate.side = side
            if contest is not None: debate.contest = contest
            if tags is not None:
                tag_names = tags.split('$') if isinstance(tags, str) else tags
                tag_names = [t for t in tag_names if t]
                matched_tags = db.query(Tag).filter(Tag.name.in_(tag_names), Tag.contest == debate.contest).all()
                debate.tags = matched_tags

def delete_data(debate_id):
    with db_session() as db:
        debate = db.query(Debate).filter(Debate.id == int(debate_id)).first()
        if debate:
            db.delete(debate)

def get_debate_history(debate_id):
    from .models import DebateHistory
    with db_session() as db:
        histories = db.query(DebateHistory).filter(DebateHistory.debate_id == int(debate_id)).order_by(DebateHistory.changed_at.desc()).all()
        ret = []
        for h in histories:
            ret.append({
                "changed_at": h.changed_at.strftime("%Y-%m-%d %H:%M:%S"),
                "editor_name": h.editor.username if h.editor else "未知使用者",
                "old_title": h.title,
                "old_content": h.content,
                "old_side": h.side
            })
        return ret

# --- 筆記 (Notes) 相關操作 ---
from .models import Note, Script

def add_note(title, content, contest):
    with db_session() as db:
        note = Note(title=title, content=content, contest=contest)
        db.add(note)

def get_notes(contest):
    with db_session() as db:
        notes = db.query(Note).filter(Note.contest == contest).order_by(Note.updated_at.desc()).all()
        return [{"id": n.id, "title": n.title, "content": n.content, "created_at": n.created_at, "updated_at": n.updated_at} for n in notes]

def update_note(note_id, title, content):
    with db_session() as db:
        note = db.query(Note).filter(Note.id == int(note_id)).first()
        if note:
            note.title = title
            note.content = content

def delete_note(note_id):
    with db_session() as db:
        note = db.query(Note).filter(Note.id == int(note_id)).first()
        if note:
            db.delete(note)

# --- 稿子 (Scripts) 相關操作 ---
def add_script(title, side, content, contest):
    with db_session() as db:
        script = Script(title=title, side=side, content=content, contest=contest)
        db.add(script)

def get_scripts(contest, side=None):
    with db_session() as db:
        query = db.query(Script).filter(Script.contest == contest)
        if side and side != "全":
            query = query.filter(Script.side == side)
        scripts = query.order_by(Script.updated_at.desc()).all()
        return [{"id": s.id, "title": s.title, "side": s.side, "content": s.content, "created_at": s.created_at, "updated_at": s.updated_at} for s in scripts]

def update_script(script_id, title, side, content):
    with db_session() as db:
        script = db.query(Script).filter(Script.id == int(script_id)).first()
        if script:
            script.title = title
            script.side = side
            script.content = content

def delete_script(script_id):
    with db_session() as db:
        script = db.query(Script).filter(Script.id == int(script_id)).first()
        if script:
            db.delete(script)