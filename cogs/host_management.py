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

        if (settings.col.count_documents({"serverid":ctx.guild.id}) >= settings.configdata["host_limit"]):
            # If a server tries to add more hosts than the instance allows, abort and tell the user.
            await ctx.send(":x: You have reached the host limit. Consider deleting one before adding a new one.")
            return

        if "://" in host:
            await ctx.send(f"{ctx.author.mention} :warning: Don't specify the HTTP protocol in your host. Please only use the domain or the IP address.")
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
        mainmsg = await ctx.send("<a:loading:815077867176067072> Calibration has started for **" + host + "**. Please wait...")
        out = subprocess.Popen(['ping','-4',host,'-c','3'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT) # Ping the host 10 times
        stdout,stderr = out.communicate() # Store the output in a var
        normal = stdout.decode('utf-8') # Decode the byte object to UTF-8
        stats = self.parser.parse(dedent(normal)) # Get pingparser to parse the output into stats
        stats = json.dumps(stats.as_dict(), indent=4) # Convert the stats object to a JSON dictionary
        stats = json.loads(stats) # Load the JSON dictionary to an actual dictionary
        # If there's no result in the search, add a monitor to the db.
        settings.col.insert_one({
            "serverid":ctx.guild.id,
            "host":host,
            "timestamp":datetime.datetime.now(),
            "calibration_result":stats["rtt_avg"],
            "monitor_chan_id":None,
            "monitor_msg_id":None
        })
        await mainmsg.edit(content=":white_check_mark: Monitor successfully added for host **" + host + "**. Use `" + settings.configdata["prefix"] + "msg <#channel> " + host + "` to proceed.")
    
    @commands.command(aliases=["edit","editmonitor"])
    @commands.has_permissions(manage_guild=True)
    async def edithost(self,ctx,host=None,newhost=None):
        if host == None or newhost == None:
            # Check if the user input a host.
            await ctx.send(":warning: You must input valid hosts!")
            return
        # Check to see if the requested host is in the db.
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            # If there's a result in the search:
            settings.col.update_many({
            "serverid":ctx.guild.id,
            "host":host
        },{
            "$set":{
                "host":newhost
            }
        })
            await ctx.send(f"{ctx.author.mention} :white_check_mark: Successfully edited host.")
            return
        await ctx.send(":warning: This host isn't being monitored.")

    @commands.command(aliases=["control","recalibrate"])
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
            mainmsg = await ctx.send("<a:loading:815077867176067072> Re-calibration has started for **" + host + "**. Please wait...")
            out = subprocess.Popen(['ping','-4',host,'-c','3'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT) # Ping the host 10 times
            stdout,stderr = out.communicate() # Store the output in a var
            normal = stdout.decode('utf-8') # Decode the byte object to UTF-8
            stats = self.parser.parse(dedent(normal)) # Get pingparser to parse the output into stats
            stats = json.dumps(stats.as_dict(), indent=4) # Convert the stats object to a JSON dictionary
            stats = json.loads(stats) # Load the JSON dictionary to an actual dictionary
            # Update the monitor's info in the db with the average ping (calibration result)
            settings.col.update_many(
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
            # Create the "new monitor" embed object
            try:
                embed=discord.Embed(title="Monitor Message for " + x["alias"], description="This monitor message has just been setup. Status updates will begin momentarily.", color=0xebebeb)
            except:
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
            newvalues = {"$set":{"monitor_chan_id":channel.id,"monitor_msg_id":monitor_msg.id}}
            settings.col.update_many({"serverid":ctx.guild.id,"host":host},newvalues)
            await asyncio.sleep(5)
            await ctx.send(f"{ctx.author.mention} :white_check_mark: Monitor message successfully setup. If the host status shows up as \"Unknown\", just wait a few moments.")

    @commands.command(aliases=["stop","deletemonitor","remove"])
    @commands.has_permissions(manage_guild=True)
    async def stopmonitor(self,ctx,host=None):
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
            settings.col.delete_one({
                "serverid":ctx.guild.id,
                "host":host
            })
            await ctx.send(f"{ctx.author.mention} :white_check_mark: Successfully stopped your monitor (50%).")
            try:
                # Try to get the monitor message's channel and message
                channel = self.bot.get_channel(x["monitor_chan_id"])
                msg = await channel.fetch_message(x["monitor_msg_id"])
            except:
                # If it errors, abort and tell the user.
                await ctx.send(":x: I couldn't delete the monitor message. Do I still have access to the channel?\n\nThe monitor has been stopped regardless.")
                return
            await msg.delete()
            await ctx.send(f"{ctx.author.mention} :white_check_mark: Successfully deleted your monitor and stopped it (100%).")
            return
        await ctx.send(":warning: This host isn't being monitored.")

    @commands.command(aliases=["list","hostlist"])
    @commands.cooldown(1,10,commands.BucketType.guild)
    async def monitorlist(self,ctx):
        # Displays all the hosts being monitored in the server.
        doc = settings.col.find({
            "serverid":ctx.guild.id,
        })
        hostlist = []
        counter = 1
        for x in doc:
            try:
                hostlist.append(str(counter) + ". " + x["alias"])
            except:
                hostlist.append(str(counter) + ". " + x["host"])
            counter += 1
        hostlist = '\n'.join(hostlist)
        if len(hostlist) > 1023:
            # If the host list is too long to display in an embed field, abort.
            hostlist = "Too many to display. Consider removing some."
            return
        embed=discord.Embed(title="List of Current Monitors", description=f"Here are all hosts being monitored in **{ctx.guild.name}**.", color=0x8080c0)
        embed.set_thumbnail(url=f"{ctx.guild.icon_url}")
        embed.add_field(name="Hosts", value=hostlist, inline=False)
        embed.set_footer(text="Made by http.james#6969")
        await ctx.send(embed=embed,delete_after=300)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unhide(self,ctx,host=None):
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
            # If the requested host is in the db, remove the alias.
            settings.col.update_many({
                "serverid":ctx.guild.id,
                "host":host
            },{
                "$unset":{
                    "alias":""
                }
            }
            )
            await ctx.send(":white_check_mark: True host has been set to **Visible**.")
            return
        await ctx.send(":warning: This host isn't being monitored.")

    @commands.command(aliases=["alias"])
    @commands.has_permissions(manage_guild=True)
    async def hide(self,ctx,host=None,alias=None):
        if host == None or alias == None:
            # Check if the user input a host.
            await ctx.send(":warning: You must input a valid host!")
            return
        
        # Check to see if the requested host has been added to the db.
        doc = settings.col.find({
            "serverid":ctx.guild.id,
            "host":host
        })
        for x in doc:
            # If the requested host is in the db, add the desired alias.
            settings.col.update_many({
                "serverid":ctx.guild.id,
                "host":host
            },{
                "$set":{
                    "alias":alias
                }
            }
            )
            await ctx.send(":white_check_mark: True host has been set to **Hidden**. The alias has been set to **" + alias + "**.")
            return
        await ctx.send(":warning: This host isn't being monitored.")

def setup(bot):
    bot.add_cog(host_management(bot))