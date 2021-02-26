import discord, asyncio, pingparsing, subprocess,json,pymongo
import datetime
from discord.ext import commands,tasks
from textwrap import dedent
import settings

class host_management(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        # Re-define the bot object into the class.

    @commands.command(aliases=["newhost"])
    @commands.has_permissions(manage_guild=True)
    async def newmonitor(self,ctx,host):
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            await ctx.send(":warning: You already have a monitor setup for this host!")
            return
        settings.col.insert_one({
            "serverid":ctx.guild.id,
            "host":host,
            "timestamp":datetime.datetime.now()
        })
        await ctx.send(":white_check_mark: Monitor successfully added for host **" + host + "**.")

    @commands.command(aliases=["control"])
    @commands.has_permissions(manage_guild=True)
    async def calibrate(self,ctx,host):
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            mainmsg = await ctx.send("Calibration has started for **" + host + "**. Please wait...")
            parser = pingparsing.PingParsing()
            out = subprocess.Popen(['ping','-4',host,'-c','10'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            stdout,stderr = out.communicate()
            normal = stdout.decode('utf-8')
            stats = parser.parse(dedent(normal))
            stats = json.dumps(stats.as_dict(), indent=4)
            stats = json.loads(stats)
            settings.col.update_one(
                {
                    "serverid":ctx.guild.id,
                    "host":host
                },{
                    "$set":{
                        "calibration_result":stats["rtt_avg"]
                    }
                }
            )
            await mainmsg.edit(content=f"{ctx.author.mention} :white_check_mark: **" + host + "** has been calibrated. You may now setup a monitor message.")
            return
        await ctx.send(":warning: This host isn't being monitored!")


    @commands.command(aliases=["msg"])
    @commands.has_permissions(manage_guild=True)
    async def statusmsg(self,ctx,channel: discord.TextChannel,host):
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            try:
                test = x["calibration_result"]
            except:
                await ctx.send(":warning: You must use `" + settings.configdata["prefix"] + "calibrate <host>` before setting up a monitor message!")
                return
            embed=discord.Embed(title="Monitor Message for " + host, description="This monitor message has just been setup. Status updates will begin momentarily.", color=0xebebeb)
            embed.add_field(name="Unknown", value="Unknown", inline=True)
            embed.set_footer(text="Made by http.james#6969")
            try:
                monitor_msg = await channel.send(embed=embed)
            except:
                await ctx.send(":warning: I couldn't send a message in your specified channel. Do I have the correct permissions?")
                return
            settings.col.update_one(
                                {
                    "serverid":ctx.guild.id,
                    "host":host
                },{
                    "$set":{
                        "monitor_chan_id":channel.id,
                        "monitor_msg_id":monitor_msg.id
                    }
                }
            )
            await ctx.send(f"{ctx.author.mention} :white_check_mark: Monitor message successfully setup. If the host status shows up as \"Unknown\", just wait a few moments.")

def setup(bot):
    bot.add_cog(host_management(bot))