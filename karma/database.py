from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sqlalchemy as sql

Base = declarative_base()

def get_karma(id):
    return get_or_create(id)


def get_all_karma():
    return session.query(Karma).all()


def update_karma(id, mod):
    row = get_or_create(id)
    row.karma += mod
    session.commit()
    return row


def get_or_create(id):
    object = session.query(Karma).filter_by(discord_id=id).first()
    if not object:
        object = Karma(discord_id=id, karma=0)
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
