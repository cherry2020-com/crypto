import importlib
import warnings

import sqlalchemy as sa
import sqlalchemy_utils as sau
from SQLAlchemy import settings
from SQLAlchemy.models import ModelBase


class RecordNotFound(Exception):
    """Requested record in database was not found"""
    pass


APP = {}


def init_db():
    if 'db' in APP:
        return
    db_url = get_db_url(settings.DATABASES["default"])
    engine = sa.create_engine(db_url, echo=settings.SQL_ECHO)
    APP['db'] = engine


def get_db_url(database):
    if database["username"]:
        db_auth = "%s:%s@%s:%s" % (database["username"], database["password"],
                                   database["host"], database["port"])
    else:
        db_auth = ""
    db_url = "%s://%s/%s" % (database["drivername"], db_auth,
                             database["database"])
    return db_url


def create_db():
    db_url = get_db_url(settings.DATABASES["default"])
    engine = sa.create_engine(db_url, echo=settings.SQL_ECHO)
    if not sau.database_exists(engine.url):
        sau.create_database(engine.url)
    ModelBase.metadata.create_all(engine)
    print("simple migrate over")


if __name__ == '__main__':
    create_db()