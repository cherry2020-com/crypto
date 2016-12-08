import sqlalchemy as sa
import sqlalchemy_utils as sau
from sqlalchemy.exc import NoSuchTableError

# meta = sa.MetaData()

class RecordNotFound(Exception):
    """Requested record in database was not found"""

question = None
choice = None

async def init_db(app):
    conf = app['config']["database"]
    db_type = conf["drivername"].split("+")[0]
    if "mysql" == db_type:
        import aiomysql.sa as aiodb
    elif "postgresql" == db_type:
        import aiopg.sa as aiodb
    else:
        raise Exception("must set database config")
    engine = await aiodb.create_engine(
        db=conf['database'],
        user=conf['username'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        loop=app.loop)
    app['db'] = engine


async def close_db(app):
    app['db'].close()
    await app['db'].wait_closed()


async def get_question(conn, question_id):
    result = await conn.execute(
        question.select()
        .where(question.c.id == question_id))
    question_record = await result.first()
    if not question_record:
        msg = "Question with id: {} does not exists"
        raise RecordNotFound(msg.format(question_id))
    result = await conn.execute(
        choice.select()
        .where(choice.c.question_id == question_id)
        .order_by(choice.c.id))
    choice_recoreds = await result.fetchall()
    return question_record, choice_recoreds


async def vote(conn, question_id, choice_id):
    result = await conn.execute(
        choice.update()
        .returning(*choice.c)
        .where(choice.c.question_id == question_id)
        .where(choice.c.id == choice_id)
        .values(votes=choice.c.votes+1))
    record = await result.fetchone()
    if not record:
        msg = "Question with id: {} or choice id: {} does not exists"
        raise RecordNotFound(msg.format(question_id), choice_id)


# 卧槽！

def create_db(app):
    global question, choice
    database = app['config']["database"]
    if database["username"]:
        db_auth = "%s:%s@%s:%s" % (database["username"], database["password"],
                                   database["host"], database["port"])
    else:
        db_auth = ""
    db_url = "%s://%s/%s" % (database["drivername"], db_auth,
                             database["database"])
    engine = sa.create_engine(db_url)
    if not sau.database_exists(engine.url):  ###确保目标数据库是存在的。
        sau.create_database(engine.url)
    metadata = sa.MetaData(bind=engine)
    try:
        question = sa.Table('users', metadata, autoload=True)
    except sa.exc.NoSuchTableError:
        question = sa.Table(
            'question', metadata,
            sa.Column('id', sa.Integer, nullable=False),
            sa.Column('question_text', sa.String(200), nullable=False),
            sa.Column('pub_date', sa.Date, nullable=False),

            # Indexes #
            sa.PrimaryKeyConstraint('id', name='question_id_pkey'))
    try:
        choice = sa.Table('users', metadata, autoload=True)
    except sa.exc.NoSuchTableError:
        choice = sa.Table(
            'choice', metadata,
            sa.Column('id', sa.Integer, nullable=False),
            sa.Column('question_id', sa.Integer, nullable=False),
            sa.Column('choice_text', sa.String(200), nullable=False),
            sa.Column('votes', sa.Integer, server_default="0", nullable=False),

            # Indexes #
            sa.PrimaryKeyConstraint('id', name='choice_id_pkey'),
            sa.ForeignKeyConstraint(['question_id'], [question.c.id],
                                    name='choice_question_id_fkey',
                                    ondelete='CASCADE'),
        )
    metadata.create_all()
    return question, choice


