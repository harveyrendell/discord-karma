import argparse
import asyncio
import platform

import discord
from discord.ext import commands

from karma.message import Message
from karma.timing import Timing
import karma.database as db
from karma import logger as logger
import karma


bot = commands.Bot(
    description='',
    command_prefix=commands.when_mentioned,
)

extensions = [
    'karma.cogs.karma',
    'karma.cogs.util',
    'karma.cogs.events',
]

@bot.event
async def on_ready():
    start_time = Timing.start()

    logger.info('Logged in as {}'.format(bot.user.name))
    logger.info('--------')
    logger.info('Karma Bot Version: {}'.format(karma.__version__))
    logger.info('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    logger.info('Startup time: {}'.format(Timing.human_readable(start_time)))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    input = Message(message)
    if input.grants_karma():
        if message.server is None:
            PM_ERROR_RESPONSE = "You know I can't do that. :wink:"
            return await bot.send_message(message.channel, PM_ERROR_RESPONSE)
        response = input.process_karma(message.author)
        return await bot.send_message(message.channel, response)

    await bot.process_commands(message)  # check if a command was called


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token', required=True, type=str)
    parser.add_argument('-d', '--db-path', type=str, default='.')
    parser.add_argument('-o', '--owner-id', type=str, default=None)
    args = parser.parse_args()
    db.init(path=args.db_path)
    bot.run(args.token)
    bot.close()


if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            logger.error('Failed to load extension {}'.format(extension))
            logger.error(e)
            raise(e)
    main()
