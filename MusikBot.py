import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def play_yt(ctx, url: str):
    """Prehrá pieseň z YouTube"""
    if not ctx.author.voice:
        await ctx.send("Prosím pripojte sa do nejakého voice kanálu.")
        return

    voice_channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await voice_channel.connect()

    # Použitie yt-dlp na získanie URL streamu
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    ffmpeg_options = {
        'options': '-vn'
    }

    voice_client.stop()  # Zastavenie predchádzajúceho prehrávania
    voice_client.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))

    await ctx.send(f"Prehrávam: {info['title']}")

@bot.command()
async def stop_play(ctx):
    """Zastaví prehrávanie"""
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Prehrávanie zastavené.")

@bot.command()
async def disconnect(ctx):
    """Odpojí bota z voice kanálu"""
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Bot bol odpojený.")

bot.run("TVOJ_BOT_TOKEN")