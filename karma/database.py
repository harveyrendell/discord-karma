from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sqlalchemy as sql

Base = declarative_base()

def get_karma(uid):
    return get_or_create(uid)


def get_all_karma():
    return session.query(Karma).all()


def update_karma(uid, mod):
    row = get_or_create(uid)
    row.karma += mod
    session.commit()
    return row


def get_or_create(uid):
    object = session.query(Karma).filter_by(discord_id=uid).first()
    if not object:
        object = Karma(discord_id=uid, karma=0)
        session.add(object)
    return object


class Karma(Base):
    __tablename__ = 'karma'
    discord_id = Column(String, primary_key=True)
    karma = Column(Integer)


engine = sql.create_engine('sqlite:///karma.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
