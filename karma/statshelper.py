from datetime import datetime, timedelta

import karma.database as db
from karma import timing

def get_karma_given_total(uid, raw_events=None):
    if not raw_events:
        raw_events = db.get_karma_given_raw(uid)
    return get_karma_total_from_events(raw_events)

def get_karma_given_dates(uid, raw_events=None):
    if not raw_events:
        raw_events = db.get_karma_given_raw(uid)
    return get_date_range_from_events(raw_events)

def get_karma_given_breakdown(uid, raw_events=None):
    if not raw_events:
        raw_events = db.get_karma_given_raw(uid)
    return get_karma_breakdown_from_events(raw_events, "user_id");

def get_karma_positive_impact(uid, given_breakdown=None):
    if not given_breakdown:
        given_breakdown = get_karma_given_breakdown(uid)
    return list(filter(lambda ele: ele["totals"]["positive"] > ele["totals"]["negative"], given_breakdown))

def get_karma_received_total(uid, raw_events=None):
    if not raw_events:
        raw_events = db.get_karma_received_raw(uid)
    return get_karma_total_from_events(raw_events)

def get_karma_received_dates(uid, raw_events=None):
    if not raw_events:
        raw_events = db.get_karma_received_raw(uid)
    return get_date_range_from_events(raw_events)

def get_karma_received_breakdown(uid, raw_events=None):
    if not raw_events:
        raw_events = db.get_karma_received_raw(uid)
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
