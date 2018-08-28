import re
import discord
from discord.ext import commands
import math

from karma import logger as logger
import karma.database as db


class Karma:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Get karma for specified users.')
    async def get(self, *args):
        logger.info("Command invoked: get | {}".format(*args))
        pattern = re.compile(r'<@!?(?P<user_id>\d+)>')

        for key in args:
            match = pattern.search(key)
            if match:
                entry = db.get_karma(match.group('user_id'))
                await self.bot.say('<@%s> has %d total karma' % (entry.discord_id, entry.karma))
            else:
                await self.bot.say('Could not find user: {}'.format(key))


    @commands.command(pass_context=True, help='Get karma for all users.')
    async def all(self, ctx):
        logger.info("Command invoked: all")

        server = ctx.message.server
        result = db.get_all_karma()
        sorted_karma = sorted(result, key=lambda k: k.karma, reverse=True)
        response = karma_summary(sorted_karma, server)

        await self.bot.say(embed=response)


    @commands.command(pass_context=True, help='Get X users with the most karma.')
    async def top(self, ctx, count=3):
        logger.info("Command invoked: top | {}".format(count))

        server = ctx.message.server
        result = db.get_all_karma()
        sorted_karma = sorted(result, key=lambda k: k.karma, reverse=True)
        response = karma_summary(sorted_karma, server, count=count)

        await self.bot.say(embed=response)


def karma_summary(items, server, count=None):
    if not count:
        count = len(items)
    items = items[:count]  # trim list if requested

    user_list = []

    for pos, user in enumerate(items, start=1):
        member = server.get_member(user.discord_id)
        if member:
            logger.info("Found member: {} ({})".format(member.name, member.id))
            line = '({}) **{:24}**'.format(
                    user.karma,
                    member.name
            )
            user_list.append(line)

    output = discord.Embed(
            title='Karma Summary',
            description=iconise_list(user_list),
            colour=discord.Colour.purple()
            )
    if count > len(items):
        output.description += '\n\n*No more entries available*'
    return output


def iconise_list(lines):
    total_length = len(lines)
    icons = []

    for i in range(total_length):
        if i is 1:
            icon = ':sparkles:'
        elif i >= max(2, round(0.1 * total_length)):
            icon = ':star2:'
        elif i >= max(3, round(0.3 * total_length)):
            icon = ':star:'
        elif i >= max(4, round(0.5 * total_length)):
            icon = ':white_sun_cloud:'
        elif i >= max(5, round(0.9 * total_length)):
            icon = ':cloud:'
        elif i >= max(6, round(0.95 * total_length)):
            icon = ':cloud_rain:'
        else:
            icon = ':thunder_cloud_rain:'
        lines[i-1] = icon + ' ' + lines[i-1]
    return '\n'.join(lines)

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Karma(bot))
