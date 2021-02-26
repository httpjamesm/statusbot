import discord, asyncio, pingparsing, subprocess,json,time
from datetime import datetime
from discord.ext import commands,tasks
from textwrap import dedent
import settings

class pinger(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.pinghost.start()
        # Re-define the bot object into the class.

    parser = pingparsing.PingParsing() # Define the ping parser function

    @tasks.loop(seconds=60)
    async def pinghost(self):
        # This will continuously ping all the hosts and update status muessages.
        doc = settings.col.find() # Find all host entries.
        for x in doc:
            try:
                # Check to see if the host entry has a calibration result and a monitor message ID stored.
                test = x["calibration_result"]
                test = x["monitor_chan_id"]
            except:
                # If either one of the results were not found, continue to the next entry.
                continue
            out = subprocess.Popen(['ping','-4',x["host"],'-c','1'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT) # Ping the host once.
            stdout,stderr = out.communicate() # Store the ping output into a var
            normal = stdout.decode('utf-8') # Decode the bytes object to UTF-8
            stats = self.parser.parse(dedent(normal)) # Parse the ping output to a stats object
            stats = json.dumps(stats.as_dict(), indent=4) # Convert the stats object to a JSON dictionary
            stats = json.loads(stats) # Convert the JSON dictionary to a real JSON dictionary
            try:
                # Try to get the monitor message's channel and message
                channel = self.bot.get_channel(x["monitor_chan_id"])
                msg = await channel.fetch_message(x["monitor_msg_id"])
            except:
                # If it errors, move onto the next host.
                continue
            now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") # Get the current time and format it
            if stats["rtt_avg"] == None: # If the ping resulted in a failure
                embed=discord.Embed(title=x["host"] + " is offline.", description="The host is unresponsive.", color=0xff0000)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Antu_dialog-error.svg/1024px-Antu_dialog-error.svg.png")
                embed.set_footer(text="Last Updated: " + now + " | http.james#6969")
                await msg.edit(embed=embed)
            elif stats["rtt_avg"] > 0 and stats["rtt_avg"] < x["calibration_result"]+50: # If the server is online and the ping is not abnormally high
                embed=discord.Embed(title=x["host"] + " is online.", description="The host is online and reachable.", color=0x00b900)
                embed.set_thumbnail(url="http://www.clker.com/cliparts/f/O/f/X/U/r/check-mark-button-hi.png")
                embed.add_field(name="Details", value="Ping to **" + x["host"] + "**: " + str(stats["rtt_avg"]) + " ms", inline=True)
                embed.set_footer(text="Last Updated: " + now + " | http.james#6969")
                await msg.edit(embed=embed)
            elif stats["rtt_avg"] < x["calibration_result"]+50: # If the ping is abnormally high
                embed=discord.Embed(title=x["host"] + " is experiencing degraded performance.", description="The host is online and reachable, but its response time is abnormally high. Users may experience degraded performance.", color=0xff8040)
                embed.set_thumbnail(url="https://www.clker.com/cliparts/P/z/K/L/2/8/yellow-warning-md.png")
                embed.add_field(name="Details", value="Ping to **" + x["host"] + "**: " + str(stats["rtt_avg"]) + " ms\n" + "Calibration Result: " + str(x["calibration_result"]) + " ms", inline=True)
                embed.set_footer(text="Last Updated: " + now + " | http.james#6969")
                await msg.edit(embed=embed)
    
def setup(bot):
    bot.add_cog(pinger(bot))