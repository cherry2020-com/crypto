from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa


ModelBase = declarative_base()


class ZhuanKe(ModelBase):
    __tablename__ = 'zhuan_ke'

    id = sa.Column(sa.String(50), primary_key=True, nullable=False)
    title = sa.Column(sa.String(255), nullable=False)
    url = sa.Column(sa.String(500), nullable=False)
    type = sa.Column(sa.Enum('hot', 'new', 'mhot'))
    is_send = sa.Column(sa.Boolean(), nullable=False, index=True)
    created_on = sa.Column(sa.DATETIME(), nullable=False,
                           server_default=sa.func.now(),
                           onupdate=sa.func.now())
    modified_on = sa.Column(sa.DATETIME(), nullable=False,
                            server_default=sa.func.now(),
                            onupdate=sa.func.now())

