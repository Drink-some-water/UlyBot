import discord
from discord.ext import commands
import aiohttp
import base64
import os

TOKEN = os.environ["DISCORD_TOKEN"]
FASTAPI_URL = "http://localhost:8000/get-files"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("Joined voice channel.")
    else:
        await ctx.send("You must be in a voice channel first.")

@bot.command(name="play")
async def play(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        await ctx.send("Bot is not in a voice channel.")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(FASTAPI_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                files = data.get("files", [])
                if not files:
                    await ctx.send("No MP3 files found.")
                    return

          
                file_data = files[0]
                filename = file_data["filename"]
                content = base64.b64decode(file_data["content"])

                with open("temp.mp3", "wb") as f:
                    f.write(content)

                voice_client.play(discord.FFmpegPCMAudio("temp.mp3"))
                await ctx.send(f"Now playing: {filename}")
            else:
                await ctx.send("Failed to fetch files from the server.")

@bot.command(name="leave")
async def leave(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

bot.run(TOKEN)
