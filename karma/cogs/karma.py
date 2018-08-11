import re
import discord
from discord.ext import commands

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
    icon = ':star:'

    for pos, user in enumerate(items, start=1):
        member = server.get_member(user.discord_id)
        if member:
            logger.info("Found member: {} ({})".format(member.name, member.id))
            line = '{} (`{}`) **{:24}**'.format(
                    icon,
                    user.karma,
                    member.name
            )
            user_list.append(line)

    output = discord.Embed(
            title='Karma Summary',
            description='\n'.join(user_list),
            colour=discord.Colour.purple()
            )
    if count > len(items):
        output.description += '\n\n*No more entries available*'
    return output


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Karma(bot))
