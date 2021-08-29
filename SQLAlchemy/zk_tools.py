import hashlib

from sqlalchemy.orm import Session
import sqlalchemy as sa

from SQLAlchemy.models import ZhuanKe
from SQLAlchemy.tools import init_db, APP


def save_data(type, title, url):
    assert type in ('hot', 'mhot', 'new')
    init_db()
    insert_id = hashlib.md5(title).hexdigest()
    insert_data = ZhuanKe(id=insert_id, title=title, type=type, is_send=False, url=url)
    session = Session(APP['db'])
    try:
        row = session.query(ZhuanKe).filter(ZhuanKe.id == insert_id).first()
        if row is None:
            session.add(insert_data)
            session.commit()
    except:
        raise
    finally:
        session.close()


def get_message():
    init_db()
    session = Session(APP['db'])
    message = []
    try:
        rows = session.query(ZhuanKe).filter(ZhuanKe.is_send == False)
        for row in rows:
            message.append({'id': row.id, 'title': row.title, 'url': row.url})
    except:
        raise
    finally:
        session.close()
    return message


def set_send(ids):
    init_db()
    session = Session(APP['db'])
    try:
        # session.query(ZhuanKe).filter(ZhuanKe.id == ids).update({ZhuanKe.is_send: True})
        session.query(ZhuanKe).filter(ZhuanKe.id.in_(ids)).update({ZhuanKe.is_send: True})
        session.commit()
    except:
        raise
    finally:
        session.close()


save_data('hot', '123321', 'http://url')
msgs = get_message()

set_send((msgs[0]['id'],))


