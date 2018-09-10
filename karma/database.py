import os

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sql

from karma import timing


Base = declarative_base()
session = None

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


def add_karma_event(message, karma_user_id, karma_change):
    row = KarmaEvent(
        user_id=karma_user_id,
        channel_id=message.channel.id,
        guild_id=message.server.id,
        karma_change=karma_change,
        given_by=message.author.id,
        message=message.content,
        timestamp=timing.Timing().current_time().timestamp(),
    )
    session.add(row)
    session.commit()


def get_all_karma_events():
    return session.query(KarmaEvent).all()


class Karma(Base):
    __tablename__ = 'karma'
    discord_id = Column(String, primary_key=True)
    karma = Column(Integer)


class KarmaEvent(Base):
    __tablename__ = 'karma-events'
    event_id = Column(Integer, primary_key=True)
    user_id = Column(String)
    channel_id = Column(String)
    guild_id = Column(String)
    karma_change = Column(Integer)
    given_by = Column(String)
    message = Column(String)
    timestamp = Column(Float)
    sqllite_autoincrement = True


def init(path='.'):
    global session

    db_path = os.path.join(path, 'karma.db')
    engine = sql.create_engine('sqlite:///{}'.format(db_path))
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
