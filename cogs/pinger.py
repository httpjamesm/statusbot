import discord, asyncio, pingparsing, subprocess,json,time
import requests_async as requests
from datetime import datetime
from discord.ext import commands,tasks
from textwrap import dedent

# Files
import settings
import util.ip_check

class pinger(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.pinghost.start()
        # Re-define the bot object into the class.

    parser = pingparsing.PingParsing() # Define the ping parser function
    successcodes = ["2","3","C","N"]

    @tasks.loop(seconds=30)
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
            
            # Ping
            out = subprocess.Popen(['ping','-4',x["host"],'-c','1'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT) # Ping the host once.
            stdout,stderr = out.communicate() # Store the ping output into a var
            normal = stdout.decode('utf-8') # Decode the bytes object to UTF-8
            stats = self.parser.parse(dedent(normal)) # Parse the ping output to a stats object
            stats = json.dumps(stats.as_dict(), indent=4) # Convert the stats object to a JSON dictionary
            stats = json.loads(stats) # Convert the JSON dictionary to a real JSON dictionary

            # HTTP Code
            # Only checks the HTTP code if the host is NOT an IP address.
            if util.ip_check.is_ip(x["host"]) == False:
                try:
                    request_data = await requests.get("https://" + x["host"],timeout=8,verify=False)
                    httpcode = str(request_data.status_code)
                except:
                    httpcode = "Could not be retrieved"
            else:
                httpcode = "Not Applicable"

            try:
                # Try to get the monitor message's channel and message
                channel = self.bot.get_channel(x["monitor_chan_id"])
                msg = await channel.fetch_message(x["monitor_msg_id"])
            except:
                # If it errors, move onto the next host.
                continue
            now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") # Get the current time and format it
            
            try:
                # If a host alias was set, display it.
                hostname = x["alias"]
            except:
                # If not, just use the host.
                hostname = x["host"]

            # If the ping resulted in a failure
            if stats["rtt_avg"] == None: 
                embed=discord.Embed(title=hostname + " is offline.", description="The host is unresponsive.", color=0xff0000)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Antu_dialog-error.svg/1024px-Antu_dialog-error.svg.png")
                embed.add_field(name="Details", value="Ping to **" + hostname + "**: Error\nHTTP Code: " + httpcode, inline=True)

            # If the server is online, the ping is not abnormally high and the HTTP code is in successcodes
            elif (stats["rtt_avg"] > 0) and (stats["rtt_avg"] < x["calibration_result"]+50) and (list(httpcode)[0] in self.successcodes): 
                embed=discord.Embed(title=hostname + " is online.", description="The host is online and reachable.", color=0x00b900)
                embed.set_thumbnail(url="http://www.clker.com/cliparts/f/O/f/X/U/r/check-mark-button-hi.png")
                embed.add_field(name="Details", value="Ping to **" + hostname + "**: " + str(stats["rtt_avg"]) + " ms\nHTTP Code: " + httpcode, inline=True)


            # If the ping is abnormally high and the HTTP code is not in successcodes
            elif (stats["rtt_avg"] > x["calibration_result"]+50) and (list(httpcode)[0] in self.successcodes): 
                embed=discord.Embed(title=hostname + " is experiencing degraded performance.", description="The host is online and reachable, but its response time is abnormally high. Users may experience degraded performance.", color=0xff8040)
                embed.set_thumbnail(url="https://www.clker.com/cliparts/P/z/K/L/2/8/yellow-warning-md.png")
                embed.add_field(name="Details", value="Ping to **" + hostname + "**: " + str(stats["rtt_avg"]) + " ms\n" + "Calibration Result: " + str(x["calibration_result"]) + " ms\nHTTP Code: " + httpcode, inline=True)
            
            # If the server is online but the HTTP code is not in successcodes
            elif (stats["rtt_avg"] > 0) and (list(httpcode)[0] not in self.successcodes):
                embed=discord.Embed(title=hostname + " is having issues.", description="The host is responding, but the server is outputting error codes.", color=0xFFFF00)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Antu_dialog-error.svg/1024px-Antu_dialog-error.svg.png")
                embed.add_field(name="Details", value="Ping to **" + hostname + "**: " + str(stats["rtt_avg"]) + " ms\nHTTP Code: " + httpcode, inline=True)
            
            # Failsafe
            else:
                print("[ERROR] Unhandled situation.")
                print(str(stats["rtt_avg"]))
                print(httpcode)
                return

            embed.set_footer(text="Last Updated: " + now + " | http.james#6969")
            await msg.edit(embed=embed)
    
def setup(bot):
    bot.add_cog(pinger(bot))