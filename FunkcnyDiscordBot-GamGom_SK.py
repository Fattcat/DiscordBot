import discord
from discord.ext import commands
import random
import asyncio


#
# This code works good
#


# Nastav token pre bota a názov kanála
CHANNEL_NAME = 'hlavny-chat'  # Your ChatRoom
TOKEN = 'YourDiscordServerToken'

# Definovanie náhodných textov
randomText_Ahoj = ["Ahoj", "ahoj", "cc", "Cau", "Čau !"]
NahodnyText_Zavinac_User = ["@Dvóchodca haloo ! GDOSI ca volá", "{message.author.mention} Mig0 haloo ! GDOSI ca volá"]

# Inicializácia bota
intents = discord.Intents.default()  # Používame defaultné intents
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} je pripravený a pripojený!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == CHANNEL_NAME:
        if message.content.lower() in ["ahoj", "cc", "cau"]:
            response = random.choice(randomText_Ahoj)
            await message.channel.send(response)

        # Pridajte ďalšie spracovanie správ tu

    await bot.process_commands(message)

# Spustenie bota
bot.run(TOKEN)
