import discord
from discord.ext import commands

class Util:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Display the service uptime.")
    async def uptime():
        logger.info("Command invoked - uptime")

        uptime = Timing.get_uptime_readable()
        response = 'Uptime: {}'.format(uptime)

        logger.info("Response - {}".format(response))
        await self.bot.say(response)

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Util(bot))
