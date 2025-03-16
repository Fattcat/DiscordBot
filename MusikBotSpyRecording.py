import discord
from discord.ext import commands, tasks
import datetime
import os
import wave
import asyncio
import numpy as np

TOKEN = "YOUR_BOT_TOKEN"
GUILD_ID = YOUR_GUILD_ID  # na dc chod do Advanced a zapni Developer mode (Vyvojarsky rezim)
                          # Potom chod na dc server a pravim tlacidlom klikni na nazov serveru
                          # A potom skopiruj dole "Kopirovat ID SERVERU"

intents = discord.Intents.all()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

class VoiceRecorder:
    def __init__(self):
        self.audio_data = []
        self.recording = False
        self.voice_client = None
        self.saving_task = None

    def start_recording(self, vc):
        self.voice_client = vc
        self.recording = True
        self.audio_data = []
        self.saving_task = asyncio.create_task(self.save_audio_loop())

    def stop_recording(self):
        self.recording = False
        if self.saving_task:
            self.saving_task.cancel()

    async def save_audio_loop(self):
        while self.recording:
            await asyncio.sleep(30)  # Uloženie každých 30 sekúnd
            await self.save_audio()

    async def save_audio(self):
        if not self.audio_data:
            return

        filename = datetime.datetime.now().strftime("%d.%m.%Y-%H-%M-%S") + ".wav"
        filepath = os.path.join(os.getcwd(), filename)

        pcm_data = np.concatenate(self.audio_data)
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(pcm_data.tobytes())

        self.audio_data = []  # Reset audio buffer

    def process_audio(self, data):
        if self.recording:
            self.audio_data.append(np.frombuffer(data, dtype=np.int16))

recorder = VoiceRecorder()

@bot.event
async def on_ready():
    print(f'Bot is ready and logged in as {bot.user}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        vc.start_recording(discord.sinks.WaveSink(), recorder.process_audio)
        recorder.start_recording(vc)
        await ctx.send("Spustene nah!")
        print("Spustene nahravanie zvuku\n")
    else:
        await ctx.send("Musis byt pripojeny do voice kanalu!")
        print("Musis byt pripojeny do voice kanalu!\n")
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        recorder.stop_recording()
        await ctx.voice_client.disconnect()
        await ctx.send("Bot sa odpojil a stopol nah.")
        print("BOT sa ODPOJIL a ZASTAVIL NAHRAVANIE\n")
bot.run(TOKEN)
