import os

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
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

def get_karma_given_raw(uid):
    return session.query(
                KarmaEvent.karma_change,
                KarmaEvent.timestamp,
                KarmaEvent.given_by,
                KarmaEvent.user_id
            ).filter_by(given_by=uid).order_by(KarmaEvent.timestamp).all()

def get_karma_received_raw(uid):
    return session.query(
                KarmaEvent.karma_change,
                KarmaEvent.timestamp,
                KarmaEvent.given_by,
                KarmaEvent.user_id
            ).filter_by(user_id=uid).order_by(KarmaEvent.timestamp).all()

def get_or_create(uid):
    object = session.query(Karma).filter_by(discord_id=uid).first()
    if not object:
        object = Karma(discord_id=uid, karma=0)
        session.add(object)
    return object


def add_karma_event(message, karma_user_id, karma_change, timestamp=timing.Timing().current_time().timestamp()):
    row = KarmaEvent(
        user_id=karma_user_id,
        channel_id=str(message.channel.id),
        guild_id=str(message.guild.id),
        karma_change=karma_change,
        given_by=str(message.author.id),
        message=message.content,
        timestamp=timestamp,
    )
    session.add(row)
    session.commit()


def get_all_karma_events():
    return session.query(KarmaEvent).all()

def get_all_karma_events_count():
    return session.query(func.count(KarmaEvent.event_id)).all()[0][0]  # [0]w[0]

def sync_karma():
    session.execute("""
        UPDATE karma
        SET karma = (
        	SELECT newValue
        	FROM (
        		SELECT k.discord_id, SUM(ke.karma_change) AS newValue
        		FROM [karma] k
        		INNER JOIN [karma-events] ke on k.discord_id = ke.user_id
        		GROUP BY k.discord_id
        	) AS correctValues WHERE karma.discord_id = correctValues.discord_id
        )
    """)
    session.execute('DELETE FROM karma WHERE karma IS NULL')
    session.commit()
    return

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
    engine = sql.create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
