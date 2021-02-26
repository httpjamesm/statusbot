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

    @tasks.loop(seconds=60)
    async def pinghost(self):
        doc = settings.col.find()
        for x in doc:
            try:
                test = x["calibration_result"]
                test = x["monitor_chan_id"]
            except:
                continue
            parser = pingparsing.PingParsing()
            out = subprocess.Popen(['ping','-4',x["host"],'-c','1'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            stdout,stderr = out.communicate()
            normal = stdout.decode('utf-8')
            stats = parser.parse(dedent(normal))
            stats = json.dumps(stats.as_dict(), indent=4)
            stats = json.loads(stats)
            try:
                channel = self.bot.get_channel(x["monitor_chan_id"])
                msg = await channel.fetch_message(x["monitor_msg_id"])
            except:
                continue
            now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            if stats["rtt_avg"] == None:
                embed=discord.Embed(title=x["host"] + " is offline.", description="The host is unresponsive.", color=0xff0000)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Antu_dialog-error.svg/1024px-Antu_dialog-error.svg.png")
                embed.set_footer(text="Last Updated: " + now + " | http.james#6969")
                await msg.edit(embed=embed)
            elif stats["rtt_avg"] > 0 and stats["rtt_avg"] < x["calibration_result"]+50:
                embed=discord.Embed(title=x["host"] + " is online.", description="The host is online and reachable.", color=0x00b900)
                embed.set_thumbnail(url="http://www.clker.com/cliparts/f/O/f/X/U/r/check-mark-button-hi.png")
                embed.add_field(name="Details", value="Ping to **" + x["host"] + "**: " + str(stats["rtt_avg"]) + " ms", inline=True)
                embed.set_footer(text="Last Updated: " + now + " | http.james#6969")
                await msg.edit(embed=embed)
            elif stats["rtt_avg"] < x["calibration_result"]+50:
                embed=discord.Embed(title=x["host"] + " is experiencing degraded performance.", description="The host is online and reachable, but its response time is abnormally high. Users may experience degraded performance.", color=0xff8040)
                embed.set_thumbnail(url="https://www.clker.com/cliparts/P/z/K/L/2/8/yellow-warning-md.png")
                embed.add_field(name="Details", value="Ping to **" + x["host"] + "**: " + str(stats["rtt_avg"]) + " ms\n" + "Calibration Result: " + str(x["calibration_result"]) + " ms", inline=True)
                embed.set_footer(text="Last Updated: " + now + " | http.james#6969")
                await msg.edit(embed=embed)
    


def setup(bot):
    bot.add_cog(pinger(bot))