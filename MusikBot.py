import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Nastavenie Intents
intents = discord.Intents.default()
intents.message_content = True  # Potrebné pre čítanie správ
intents.voice_states = True     # Potrebné pre kontrolu pripojenia do voice kanála

bot = commands.Bot(command_prefix="!", intents=intents)

# Príkaz na prehranie hudby z YouTube
@bot.command(name="play_yt")
async def play_yt(ctx, url: str):
    voice_channel = ctx.author.voice  # Získanie informácií o hlasovom kanáli užívateľa

    # Overenie, či je užívateľ v nejakom hlasovom kanáli
    if not voice_channel or not voice_channel.channel:
        await ctx.send("❌ **Prosím, pripojte sa do nejakého hlasového kanála!**")
        return

    # Ak už je bot pripojený k nejakému kanálu, použije ho, inak sa pripojí
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        voice_client = await voice_channel.channel.connect()

    # Stiahnutie audio streamu z YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    # Prehrávanie hudby
    voice_client.stop()
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=lambda e: print(f'Chyba pri prehrávaní: {e}') if e else None)
    await ctx.send(f"🎵 **Prehrávam:** {info['title']}")

# Spustenie bota s tokenom
bot.run(TOKEN)