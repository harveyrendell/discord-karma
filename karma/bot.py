import discord
import asyncio

import argparse
import re

from discord.ext import commands
import platform
from pydblite.pydblite import Base

DB_FILE = 'karma.db'


client = commands.Bot(
    description='',
    command_prefix='!',
)

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))


@client.event
async def on_message(message):
    pattern = re.compile('<@!?(?P<user_id>\d+)>\s?(?P<mod>[\+-]{2,})')
    match = pattern.search(message.content)

    if match:
        mod = len(match.group('mod')) - 1  # given karma is one fewer than the number of +'es or -'es
        mod = min(mod, 3)  # limit change to 3 karma maximum
        change_type = match.group('mod')[0]
        if change_type == '-':
            mod = mod * -1

        if message.author.id == match.group('user_id'):
            reply = "Don't be a weasel!" if change_type == '+' else "Don't be so hard on yourself."
            return await client.send_message(message.channel, reply)

        update_karma(match.group('user_id'), mod)


def update_karma(user_id, mod, reason=None):
    print("Called update with %s %d %s" % (user_id, mod, reason))




parser = argparse.ArgumentParser()
parser.add_argument('-t', '--token', required=True, type=str)
args = parser.parse_args()

client.run(args.token)
