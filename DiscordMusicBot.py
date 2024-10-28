import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Konfigurácia pre yt_dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'Bot je prihlásený ako {bot.user}.')

@bot.command()
async def play(ctx, url: str):
    # Získa hlasový kanál s názvom "Channel"
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name="🔫 CS2 #1")
    
    if voice_channel is None:
        await ctx.send("Kanál s názvom 'Channel' neexistuje.")
        return

    # Ak sa bot nachádza v inom hlasovom kanáli, odpojí sa
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    # Pripojenie do určeného hlasového kanálu
    voice_client = await voice_channel.connect()

    # Prehrá pieseň z YouTube linku
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        voice_client.play(player, after=lambda e: print(f'Prehrávalo sa chyba: {e}') if e else None)

    await ctx.send(f'Prehrávam: {player.data["title"]}')

@bot.command()
async def stop(ctx):
    # Zastaví prehrávanie a odpojí sa od hlasového kanála
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bot sa odpojil z hlasového kanála.")
    else:
        await ctx.send("Bot nie je pripojený k žiadnemu hlasovému kanálu.")

# Token bota (nájdete na stránke Discord Developers)
bot.run('TOKEN')
