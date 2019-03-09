import argparse
import tzlocal
from datetime import datetime
from dateutil.relativedelta import relativedelta

import discord

import random

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import karma.database as db
from karma import logger as logger

# collection of users to interact
community = [
    '174776038478446592',
    '484012271916548109',
    '474801853553442837',
    '397263385202393099',
    '491368352682344469',
    '489470624243253259',
    '491141794122432513'
]

# collection of messages to randomly use
messages = [
    "",
    "thanks for the sauce",
    "lul and kek",
    "good response",
    "high quality content",
    "good shit thats some good shit right there",
    "worth the read, gilded xd",
    "repost from animemes but better the second time"
]

server = discord.Server(id="330444403044909067")
channel = discord.Channel(server=server, id="553786725626019840")

def get_votes():
    roll = random.random()
    value = 0
    if roll >= 0.95:
        value = 3
    elif roll >= 0.75:
        value = 2
    elif roll >= 0.25:
        value = 1
    return value

def main():
    logger.info('Generating data ...')
    timezone = tzlocal.get_localzone()
    end_time = timezone.localize(datetime.now())
    start_time = end_time - relativedelta(weeks=5)
    current_time = start_time

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db-path', type=str, default='.')
    args = parser.parse_args()
    db.init(path=args.db_path)
    while current_time < end_time:
        for person in community:
            todays_roll = get_votes()
            for x in range(todays_roll):
                # Select a random person ...
                without = list(community)
                without.remove(person)
                giver = random.choice(without)
                message = discord.Message(
                    content='{} <@{}>++'.format(random.choice(messages), person),
                    channel=channel,
                    server=server,
                    author={"id": giver},
                    reactions=[]
                )
                db.update_karma(person, 1)
                db.add_karma_event(
                    message,
                    person,
                    1,
                    current_time.timestamp()
                )
            logger.info('Current person {} assigned {} karma at {}>'.format(person, todays_roll, current_time))
        current_time += relativedelta(days=1)
        logger.info('New time is {}'.format(current_time))

if __name__ == "__main__":
    main()
