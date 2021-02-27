import discord,time,json
from discord.ext import commands
import settings

class listeners(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        # Re-define the bot object into the class.

    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        print('[INFO] Logged in')
        print("[INFO] Username:",self.bot.user)
        print("[INFO] User ID:",self.bot.user.id)
        await self.bot.change_presence(activity=discord.Game(name=settings.configdata["prefix"] + "help"))
        print("[Start] Presence updated")
    
    @commands.Cog.listener('on_message')
    async def on_message(self,message):
        if self.bot.user in message.mentions:
            await message.channel.send(f":wave: Hi **{message.author.display_name}**! My command prefix is **" + settings.configdata["prefix"] + "**. Use **" + settings.configdata["prefix"] + "help** for usage details.")

def setup(bot):
    bot.add_cog(listeners(bot))