import argparse
import asyncio
import platform
import re

import discord
from discord.ext import commands

import database as db

DB_FILE = 'karma.db'


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
    await client.process_commands(message)  # check if command has been called

    pattern = re.compile(r'<@!?(?P<user_id>\d+)>\s?(?P<mod>[\+-]{2,})')
    match = pattern.search(message.content)

    if match:
        mod = len(match.group('mod')) - 1  # given karma is one fewer than the number of +'es or -'es
        mod = min(mod, 3)  # limit change to 3 karma maximum
        change_type = match.group('mod')[0]
        if change_type == '-':
            mod = mod * -1

        if message.author.id == match.group('user_id'):
            response = "Don't be a weasel!" if change_type == '+' else "Don't be so hard on yourself."
            return await client.send_message(message.channel, response)

        user_id = match.group('user_id')
        entry = db.update_karma(user_id, mod)
        change = 'increased' if mod > 0 else 'decreased'

        response = "<@%s>'s karma has %s to %d" % (user_id, change, entry.karma)
        await client.send_message(message.channel, response)


@client.command(help="check if I'm alive, yo")
async def ping():
    await client.say('Beep boop')


@client.command(help='get karma for specified user')
async def get(user: str):
    print('called getkarma with %s' % user)
    pattern = re.compile(r'<@!?(?P<user_id>\d+)>')
    match = pattern.search(user)
    if match:
        entry = db.get_karma(match.group('user_id'))
        await client.say('<@%s> has %d total karma' % (entry.discord_id, entry.karma))


@client.command(pass_context=True, help='get karma for every user')
async def all(ctx):
    result = db.get_all_karma()
    server = ctx.message.server
    output_lines = []

    output_lines.append('Karma Summary:')
    output_lines.append('```')
    output_lines += [
        '%s %3d' % (server.get_member(entry.discord_id).name.ljust(20), entry.karma)
        for entry in result
    ]
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
