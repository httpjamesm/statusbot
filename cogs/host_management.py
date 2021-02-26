import discord, asyncio, pingparsing, subprocess,json,pymongo
import datetime
from discord.ext import commands,tasks
from textwrap import dedent
import settings

class host_management(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        # Re-define the bot object into the class.
    parser = pingparsing.PingParsing() # Define the ping parser function

    @commands.command(aliases=["newhost"])
    @commands.has_permissions(manage_guild=True)
    async def newmonitor(self,ctx,host=None):
        if host == None:
            # Check if the user input a host.
            await ctx.send(":warning: You must input a valid host!")
            return

        # Check to see if the requested host is not a duplicate.
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            # If there's a result in the search:
            await ctx.send(":warning: You already have a monitor setup for this host!")
            return
        # If there's no result in the search, add a monitor to the db.
        settings.col.insert_one({
            "serverid":ctx.guild.id,
            "host":host,
            "timestamp":datetime.datetime.now()
        })
        await ctx.send(":white_check_mark: Monitor successfully added for host **" + host + "**.")

    @commands.command(aliases=["control"])
    @commands.has_permissions(manage_guild=True)
    async def calibrate(self,ctx,host=None):
        if host == None:
            # Check if the user input a host.
            await ctx.send(":warning: You must input a valid host!")
            return
        
        # Check to see if the requested host has been added to the db.
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            # If there's a result in the search, begin calibration.
            mainmsg = await ctx.send("Calibration has started for **" + host + "**. Please wait...")
            out = subprocess.Popen(['ping','-4',host,'-c','10'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT) # Ping the host 10 times
            stdout,stderr = out.communicate() # Store the output in a var
            normal = stdout.decode('utf-8') # Decode the byte object to UTF-8
            stats = self.parser.parse(dedent(normal)) # Get pingparser to parse the output into stats
            stats = json.dumps(stats.as_dict(), indent=4) # Convert the stats object to a JSON dictionary
            stats = json.loads(stats) # Load the JSON dictionary to an actual dictionary
            # Update the monitor's info in the db with the average ping (calibration result)
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
        # If there's no result in the search, abort and tell the user.
        await ctx.send(":warning: This host isn't being monitored!")


    @commands.command(aliases=["msg"])
    @commands.has_permissions(manage_guild=True)
    async def statusmsg(self,ctx,channel: discord.TextChannel = None,host=None):
        if host == None or channel == None:
            # Check if the user input a text channel and host.
            await ctx.send(":warning: You must input a valid text channel and/or host!")
            return

        # Check to see if the requested host has been added to the db.
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            # If there's a result in the search:
            try:
                test = x["calibration_result"] # Test to see if the monitor has a calibration result stored
            except:
                # If no calibration result was found, abort and tell the user.
                await ctx.send(":warning: You must use `" + settings.configdata["prefix"] + "calibrate <host>` before setting up a monitor message!")
                return
            # Create the "new monitor" embed object
            embed=discord.Embed(title="Monitor Message for " + host, description="This monitor message has just been setup. Status updates will begin momentarily.", color=0xebebeb)
            embed.add_field(name="Unknown", value="Unknown", inline=True)
            embed.set_footer(text="Made by http.james#6969")
            try:
                # Try to send the monitor message in the desired channel
                monitor_msg = await channel.send(embed=embed)
            except:
                # If the bot couldn't send the message, ask the user for help.
                await ctx.send(":warning: I couldn't send a message in your specified channel. Do I have the correct permissions?")
                return
            # If the message was sent successfully, store the message details to refer to it later.
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