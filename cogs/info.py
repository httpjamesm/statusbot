import discord,time,json
from discord.ext import commands
import settings

class info(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        # Re-define the bot object into the class.

    @commands.command(aliases=["about","info"])
    @commands.cooldown(1,10,commands.BucketType.user)
    async def help(self,ctx):
        embed=discord.Embed(title="StatusBot Help", description="StatusBot is a Discord bot that can create real-time status pages within Discord communities for any host that supports IPv4 connectivity.\n\nYou can invoke this menu at anytime using `" + settings.configdata["prefix"] + "help`.", color=0xff0000)
        embed.add_field(name="Instance", value="**Name**: " + settings.configdata["instance_name"] + "\nMonitor Limit: " + str(settings.configdata["host_limit"]), inline=False)
        embed.add_field(name="Host Management", value="Use **" + settings.configdata["prefix"] + "** as the prefix for the following commands.\n\n`newhost <host>` - Create a new host monitor.\n`calibrate <host>` - Re-calibrate the baseline ping for your host.\n`msg <#channel> <host>` - Setup a monitor/status message.\n`edit <host> <new host>` - Edit an existing host.\n`hide <host> <alias>` - Hide the host's true identity with an alias. Useful for hiding internal IPs.\n`stop <host>` - Delete a host.", inline=True)
        embed.add_field(name="Developers", value="Are you a developer? You can improve this project at the official Github page:\nhttps://github.com/httpjamesm/statusbot",inline=False)
        embed.set_footer(text="Made by http.james#6969")
        try:
            await ctx.author.send(embed=embed)
        except:
            await ctx.send(f"{ctx.author.mention} :warning: I couldn't send you a DM, do you have DMs enabled?")
            return
        await ctx.send(f"{ctx.author.mention} :white_check_mark: I've sent you a DM!")

    @commands.command(aliases=["latency"])
    @commands.cooldown(1,10,commands.BucketType.guild)
    async def ping(self,ctx):
        await ctx.send(":ping_pong: Pong! API Latency: " + str(round(self.bot.latency*100,2)) + " ms.")

def setup(bot):
    bot.add_cog(info(bot))