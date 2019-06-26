import os

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
import sqlalchemy as sql

from datetime import datetime, timedelta
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
            ).filter_by(given_by=uid).\
            order_by(KarmaEvent.timestamp).\
            all()

def get_karma_given_total(uid, raw_events=None):
    if not raw_events:
        raw_events = get_karma_given_raw(uid)
    return get_karma_total_from_events(raw_events)

def get_karma_given_dates(uid, raw_events=None):
    if not raw_events:
        raw_events = get_karma_given_raw(uid)
    return get_date_range_from_events(raw_events)

def get_karma_given_breakdown(uid, raw_events=None):
    if not raw_events:
        raw_events = get_karma_given_raw(uid)
    return get_karma_breakdown_from_events(raw_events, "user_id");

def get_karma_positive_impact(uid, given_breakdown=None):
    if not given_breakdown:
        given_breakdown = get_karma_given_breakdown(uid)
    return list(filter(lambda ele: ele["totals"]["positive"] > ele["totals"]["negative"], given_breakdown))

def get_karma_received_raw(uid):
    return session.query(
                KarmaEvent.karma_change,
                KarmaEvent.timestamp,
                KarmaEvent.given_by,
                KarmaEvent.user_id
            ).filter_by(user_id=uid).\
            order_by(KarmaEvent.timestamp).\
            all()

def get_karma_received_total(uid, raw_events=None):
    if not raw_events:
        raw_events = get_karma_received_raw(uid)
    return get_karma_total_from_events(raw_events)

def get_karma_received_dates(uid, raw_events=None):
    if not raw_events:
        raw_events = get_karma_received_raw(uid)
    return get_date_range_from_events(raw_events)

def get_karma_received_breakdown(uid, raw_events=None):
    if not raw_events:
        raw_events = get_karma_received_raw(uid)
    return get_karma_breakdown_from_events(raw_events, "given_by");

def get_karma_breakdown_from_events(events, attr):
    breakdowns = {}
    for event in events:
        attr_val = getattr(event, attr)
        if attr_val not in breakdowns:
            breakdowns[attr_val] = {
                "positive" : 0,
                "negative" : 0
            }
        update_karma_dict(breakdowns[attr_val], event)

    breakdowns_list = []
    for key, value in breakdowns.items():
        breakdowns_list.append({"discord_id" : key, "totals" : value})
    return breakdowns_list

def get_karma_total_from_events(events):
    diff = {
        "positive" : 0,
        "negative" : 0
    }

    for event in events:
        update_karma_dict(diff, event)

    return diff

def get_date_range_from_events(events):
    if not events:
        return []

    first = timestamp_to_datetime(events[0].timestamp)
    last =  timestamp_to_datetime(events[-1].timestamp)

    date_range = [{ "date" : (first + timedelta(days=x)).date(), "diff": {
        "positive" : 0,
        "negative" : 0
    } } for x in range((last - first).days + 2)] # Because of the way date diffs work we may need an extra day buffer
    current_index = 0
    for event in events:
        while date_range[current_index]["date"] != timestamp_to_datetime(event.timestamp).date():
            current_index += 1
        update_karma_dict(date_range[current_index]["diff"], event)

    return date_range

def update_karma_dict(dict, event):
    if event.karma_change > 0:
        dict["positive"] += event.karma_change
    else:
        dict["negative"] += abs(event.karma_change);

def timestamp_to_datetime(timestamp):
    return timing.Timing.timezone.localize(datetime.fromtimestamp(float(timestamp)))

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
    engine = sql.create_engine('sqlite:///{}'.format(db_path))
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
