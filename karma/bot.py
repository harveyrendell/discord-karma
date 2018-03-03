import argparse
import asyncio
import logging
import platform
import re
import sys

import discord
from discord.ext import commands

import database as db
from message import Message

DB_FILE = 'karma.db'

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

formatter = logging.Formatter('[%(levelname)s]: %(message)s')
handler = logging.StreamHandler(sys.stdout)

handler.setFormatter(formatter)
logger.addHandler(handler)


client = commands.Bot(
    description='',
    command_prefix='karma ',
    pm_help=True
)

@client.event
async def on_ready():
    print('Logged in as {}'.format(client.user.name))
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))


@client.event
async def on_message(message):
    await client.process_commands(message)  # check if a command was called

    input = Message(message)
    if input.grants_karma():
        response = input.process_karma()
        return await client.send_message(message.channel, response)


@client.command(help="check if I'm alive, yo")
async def ping():
    await client.say('Beep boop')


@client.command(help='get karma for specified user')
async def get(user: str):
    logger.info('called get with %s' % user)
    pattern = re.compile(r'<@!?(?P<user_id>\d+)>')
    match = pattern.search(user)
    if match:
        entry = db.get_karma(match.group('user_id'))
        await client.say('<@%s> has %d total karma' % (entry.discord_id, entry.karma))


@client.command(pass_context=True, help='get karma for every user')
async def all(ctx):
    output_lines = []
    server = ctx.message.server
    result = db.get_all_karma()
    sorted_karma = sorted(result, key=lambda k: k.karma, reverse=True)

    output_lines.append('Karma Summary:')
    output_lines.append('```')

    for pos, user in enumerate(sorted_karma, start=1):
        karma = user.karma
        name = server.get_member(user.discord_id).name
        output_lines.append('{:4d}. {:.<20s} {}'.format(pos, name, karma))

    output_lines.append('```')
    response = '\n'.join(output_lines)
    await client.say(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True, type=str)
    args = parser.parse_args()
    client.run(args.token)


if __name__ == "__main__":
    main()
