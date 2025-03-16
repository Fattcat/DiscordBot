import discord
from discord.ext import commands
import yt_dlp
import asyncio

TOKEN = "Your Token HERE"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def play_yt(ctx, url: str):
    if ctx.channel.name != "music-chat":
        await ctx.send("❌ Tento príkaz môžeš používať len v #music-chat kanáli.")
        return
    
    voice_channel = ctx.author.voice.channel if ctx.author.voice else None
    if not voice_channel:
        await ctx.send("❌ Musíš byť v hlasovom kanáli!")
        return
    
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not vc:
        vc = await voice_channel.connect()
    
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'noplaylist': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
    
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    
    vc.stop()
    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options), after=lambda e: print(f'Prehrávanie skončené: {e}'))
    await ctx.send(f'🎶 Prehrávam: **{info["title"]}**')

@bot.command()
async def stop_play(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏹️ Prehrávanie zastavené.")
    else:
        await ctx.send("❌ Momentálne sa nič neprehráva.")

@bot.command()
async def disconnect(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc:
        await vc.disconnect()
        await ctx.send("📴 Bot odpojený z hlasového kanála.")
    else:
        await ctx.send("❌ Bot nie je pripojený k hlasovému kanálu.")

bot.run(TOKEN)
