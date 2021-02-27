import discord, datetime, json
from discord.ext import commands

# Import config info
import settings

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix=settings.configdata["prefix"],intents=intents)
bot.remove_command('help')

initial_extensions = [
    'cogs.pinger',
    'cogs.host_management',
    'cogs.info',
    'cogs.listeners'
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

bot.run(settings.configdata["token"])