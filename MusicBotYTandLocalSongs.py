import discord
from discord.ext import commands
import yt_dlp

TOKEN = "token"
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot je pripravený ako {bot.user}')

# Pomocná funkcia: pripojí bota do hlasového kanála používateľa
async def ensure_voice_connection(ctx):
    user_voice = ctx.author.voice
    if not user_voice or not user_voice.channel:
        await ctx.send("❌ Musíš byť pripojený do hlasového kanála.")
        return None

    voice_channel = user_voice.channel
    existing_vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if existing_vc:
        if existing_vc.channel != voice_channel:
            await existing_vc.disconnect()
            existing_vc = await voice_channel.connect()
    else:
        existing_vc = await voice_channel.connect()

    return existing_vc

@bot.command()
async def play_yt(ctx, url: str):
    if ctx.channel.name != "music-chat":
        await ctx.send("❌ Tento príkaz môžeš používať len v music-chat kanáli.")
        return

    vc = await ensure_voice_connection(ctx)
    if not vc:
        return

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
    except Exception as e:
        await ctx.send(f"❌ Chyba pri načítaní videa: {e}")
        return

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    vc.stop()
    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
            after=lambda e: print(f'Prehrávanie skončené: {e}'))
    await ctx.send(f'🎶 Prehrávam: **{info["title"]}**')

@bot.command()
async def play_local(ctx, filename: str):
    if ctx.channel.name != "music-chat":
        await ctx.send("❌ Tento príkaz môžeš používať len v music-chat kanáli.")
        return

    vc = await ensure_voice_connection(ctx)
    if not vc:
        return

    filepath = filename.strip()
    try:
        ffmpeg_options = {
            'options': '-vn -ar 48000 -ac 2'
        }
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(filepath, **ffmpeg_options),
                after=lambda e: print(f'Prehrávanie skončené: {e}'))
        await ctx.send(f'🎵 Prehrávam lokálny súbor: **{filepath}**')
    except Exception as e:
        await ctx.send(f"❌ Nepodarilo sa prehrať súbor: {e}")

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