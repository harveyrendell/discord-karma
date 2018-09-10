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

    @commands.command(pass_context=True, help="[DISABLED] Get all karma events.")
    async def get_events(self, ctx):
        return # Don't execute command

        events = db.get_all_karma_events()
        for event in events:
            guild = self.bot.get_server(event.guild_id)
            giver_user = guild.get_member(event.given_by) or 'Unknown User'
            receiver_user = guild.get_member(event.user_id)
            giver_avatar_url = giver_user.avatar_url or giver_user.default_avatar_url
            receiver_avatar_url = receiver_user.avatar_url or receiver_user.default_avatar_url

            embed = discord.Embed(
                timestamp = Timing.timezone.localize(datetime.fromtimestamp(float(event.timestamp))),
                colour=discord.Colour.purple(),
                description=event.message,
            )
            embed.set_footer(
                text=f'Given by {giver_user.display_name}',
                icon_url=giver_avatar_url)

            await self.bot.send_message(ctx.message.channel, embed=embed)


# The setup function below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Events(bot))
