import discord,time,json
from discord.ext import commands
import settings

class info(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        # Re-define the bot object into the class.

    @commands.command(aliases=["about","info"])
    async def help(self,ctx):
        embed=discord.Embed(title="StatusBot Help", description="StatusBot is a Discord bot that can create real-time status pages within Discord communities for any host that supports IPv4 connectivity.\n\nYou can invoke this menu at anytime using `" + settings.configdata["prefix"] + "help`.", color=0xff0000)
        embed.add_field(name="Instance", value="**Name**: " + settings.configdata["instance_name"], inline=False)
        embed.add_field(name="Host Management", value="Use **" + settings.configdata["prefix"] + "** as the prefix for the following commands.\n\n`newhost <host>` - Create a new host monitor.\n`calibrate <host>` - Calibrate the baseline ping for your host.\n`msg <#channel> <host>` - Setup a monitor/status message.", inline=True)
        embed.set_footer(text="Made by http.james#6969")
        try:
            await ctx.author.send(embed=embed)
        except:
            await ctx.send(f"{ctx.author.mention} :warning: I couldn't send you a DM, do you have DMs enabled?")
            return
        await ctx.send(f"{ctx.author.mention} :white_check_mark: I've sent you a DM!")

def setup(bot):
    bot.add_cog(info(bot))