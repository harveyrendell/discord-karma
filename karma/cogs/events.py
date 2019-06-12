import logging
from datetime import datetime

import discord
from discord.ext import commands

import karma.database as db
from karma.timing import Timing

logger = logging.getLogger(__name__)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="[DISABLED] Get all karma events.")
    async def get_events(self, ctx):
        return # Don't execute command

        events = db.get_all_karma_events()
        for event in events:
            guild = self.bot.get_guild(int(event.guild_id))
            giver_user = guild.get_member(int(event.given_by))
            receiver_user = guild.get_member(int(event.user_id))
            giver_avatar_url = giver_user.avatar_url or giver_user.default_avatar_url if giver_user != None else None
            receiver_avatar_url = receiver_user.avatar_url or receiver_user.default_avatar_url if receiver_user != None else None
            embed = discord.Embed(
                timestamp = Timing.timezone.localize(datetime.fromtimestamp(float(event.timestamp))),
                colour=discord.Colour.purple(),
                description=event.message,
            )

            footer_text = 'Given by {}'.format(giver_user.display_name if giver_user != None else 'Unknown User')
            if giver_avatar_url != None:
                embed.set_footer(
                    text=footer_text,
                    icon_url=giver_avatar_url
                )
            else:
                embed.set_footer(text=footer_text)

            await ctx.send(embed=embed)


# The setup function below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Events(bot))
