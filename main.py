import discord, datetime, json
from discord.ext import commands

# Import config info
import settings

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=settings.configdata["prefix"],intents=intents)
bot.remove_command('help')
bot.launch_time = datetime.datetime.now()
print("[Start] Launch time defined")

initial_extensions = [
    'cogs.pinger',
    'cogs.host_management'
]

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e: 
            print("[!! ERROR] " + extension + " could not be loaded.\n\nError below:\n")
            print(e)
            continue
    print("[Start] Cogs initialized")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print('[INFO] Logged in')
    print("[INFO] Username:",bot.user)
    print("[INFO] User ID:",bot.user.id)
    await bot.change_presence(activity=discord.Game(name="sb?help"))
    print("[Start] Presence changed")

bot.run(settings.configdata["token"])