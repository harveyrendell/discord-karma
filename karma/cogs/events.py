import logging
from datetime import datetime

import discord
from discord.ext import commands

import karma.database as db
from karma.timing import Timing

logger = logging.getLogger(__name__)

class Events:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, help="Get all karma events.")
    async def get_events(self, ctx):
        events = db.get_all_karma_events()
        for event in events:
            embed = discord.Embed(
                title='Karma event',
                timestamp = Timing.timezone.localize(datetime.fromtimestamp(float(event.timestamp))),
                colour=discord.Colour.purple(),
                description = event.message,
            )
            await self.bot.send_message(ctx.message.channel, embed=embed)


# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Events(bot))
