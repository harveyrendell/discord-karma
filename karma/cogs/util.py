import discord
from discord.ext import commands

from karma import logger as logger
from karma.timing import Timing

import karma.database as db

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Display the service uptime.")
    async def uptime(self, ctx):
        logger.info("Command invoked - uptime")

        uptime = Timing.get_uptime_readable()
        response = 'Uptime: {}'.format(uptime)

        logger.info("Response - {}".format(response))
        await ctx.send(response)

    @commands.command(help="Sync the karma events db with the actual karma scores.")
    async def sync(self, ctx):
        logger.info("Command invoked - sync")
        db.sync_karma()
        await ctx.send("Sync complete!")

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Util(bot))
