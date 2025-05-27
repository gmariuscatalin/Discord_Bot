import discord
from discord.ext import commands
import random
import yt_dlp
import asyncio
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

FFMPEG_PATH = os.getenv("FFMPEG_PATH")

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="poll", description="Create a poll with reactions for voting.")
    async def poll(self, interaction: discord.Interaction, question: str, option_1: str, option_2: str, option_3: str = None, option_4: str = None):
        """Creates a poll with multiple choice options."""
        options = [option_1, option_2, option_3, option_4]
        options = [opt for opt in options if opt]
        if len(options) < 2:
            await interaction.response.send_message("You need at least two options for the poll!", ephemeral=True)
            return

        poll_message = f"**Poll:** {question}\n"
        poll_message += "\n".join([f"{index+1}. {option}" for index, option in enumerate(options)])

        await interaction.response.send_message(poll_message)
        poll_msg = await interaction.original_response()

        emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        for i in range(len(options)):
            await poll_msg.add_reaction(emoji_list[i])

    @discord.app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction):
        """Says hello to the user."""
        await interaction.response.send_message(f"Hello, {interaction.user.name}!")

    @discord.app_commands.command(name="animal")
    async def animal(self, interaction: discord.Interaction):
        """Sends a random animal emoji."""
        await interaction.response.defer(thinking=True)
        animals = ['🐶', '🐱', '🐭', '🦁', '🐯', '🐸', '🐼', '🐧', '🐨', '🐰']
        await interaction.followup.send(f"Here is a random animal: {random.choice(animals)}")

    @discord.app_commands.command(name="roll")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d6"):
        """Rolls a dice in NdN format (e.g. 2d6)."""
        try:
            rolls, limit = map(int, dice.lower().split('d'))
        except Exception:
            await interaction.response.send_message("Format must be in NdN format (e.g. 2d6)")
            return
        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await interaction.response.send_message(f"{interaction.user.name} rolled: {result}")

    @discord.app_commands.command(name="connect", description="Make the bot join your voice channel.")
    async def connect(self, interaction: discord.Interaction):
        """Connects the bot to the user's voice channel."""
        await interaction.response.defer()

        if not interaction.user.voice:
            await interaction.followup.send("You're not in a voice channel!", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        try:
            vc = await channel.connect(timeout=10, reconnect=True)
            if vc:
                await interaction.followup.send(f"Joined {channel.name}!")
            else:
                await interaction.followup.send("Failed to connect.", ephemeral=True)
        except discord.errors.ClientException as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)
        except discord.errors.Forbidden:
            await interaction.followup.send("I don't have permission to join voice channels!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An unexpected error occurred: {e}", ephemeral=True)

    @discord.app_commands.command(name="disconnect")
    async def disconnect(self, interaction: discord.Interaction):
        """Makes the bot leave the voice channel."""
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Disconnected from the voice channel.")
        else:
            await interaction.response.send_message("I'm not in a voice channel.")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.currently_playing = {}

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Checks if the URL is a valid YouTube or YouTube Music link."""
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and "youtube.com" in parsed.netloc

    async def get_song_info(self, url: str):
        """Fetch the title and uploader of a YouTube video or song."""
        def fetch_info():
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get("title", "Unknown Title")
                    uploader = info.get("uploader", "Unknown Uploader")
                    return title, uploader
            except yt_dlp.utils.DownloadError as e:
                print(f"Error fetching song info: {e}")
                return None, None

        return await asyncio.to_thread(fetch_info)

    @discord.app_commands.command(name="play", description="Play a song from a YouTube or YouTube Music URL.")
    async def play(self, interaction: discord.Interaction, url: str):
        """Plays a song from a YouTube or YouTube Music URL."""
        await interaction.response.defer()

        if not self.is_valid_url(url):
            await interaction.followup.send("Invalid URL provided. Please provide a valid YouTube or YouTube Music link.", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if not vc:
            if not interaction.user.voice:
                await interaction.followup.send("You must be in a voice channel to play music!", ephemeral=True)
                return
            channel = interaction.user.voice.channel
            vc = await channel.connect()

        guild_id = interaction.guild.id
        if guild_id not in self.song_queue:
            self.song_queue[guild_id] = []

        title, uploader = await self.get_song_info(url)
        if not title:
            await interaction.followup.send("Failed to fetch song info. Please try again later.", ephemeral=True)
            return

        self.song_queue[guild_id].append((url, title, uploader, interaction.user.display_name, interaction.channel))
        await interaction.followup.send(
            f"🎶 Added to queue: **{title}** by **{uploader}** (requested by {interaction.user.display_name})"
        )

        if not self.currently_playing.get(guild_id, False):
            await self._process_queue(vc, interaction.guild, interaction.channel)

    async def _process_queue(self, vc, guild, _=None):
        """Processes the song queue and plays the next song."""
        guild_id = guild.id
        if not self.song_queue.get(guild_id):
            self.currently_playing[guild_id] = False
            return

        self.currently_playing[guild_id] = True
        url, title, uploader, requested_by, text_channel = self.song_queue[guild_id].pop(0)
        filename = await self.download_song(url)

        if filename:
            # Always send "Now playing" in the original requester's channel
            if text_channel is not None:
                await text_channel.send(
                    f"Now playing: **{title}** by **{uploader}** (requested by {requested_by})"
                )
            await self._play_song(vc, guild, filename)
        else:
            await self._process_queue(vc, guild, text_channel)

    async def download_song(self, url: str):
        """Asynchronously downloads a YouTube song."""
        song_folder = "D:/Discord_Bot/Songs"
        os.makedirs(song_folder, exist_ok=True)

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "outtmpl": f"{song_folder}/%(id)s.%(ext)s",
            "ffmpeg_location": FFMPEG_PATH,
            "quiet": True
        }

        def run_yt_dlp():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return f"{song_folder}/{info['id']}.mp3"
            except Exception as e:
                print(f"Error downloading: {e}")
                return None

        return await asyncio.to_thread(run_yt_dlp)

    async def _play_song(self, vc, guild, filename):
        """Plays a downloaded song."""
        if not vc.is_connected():
            return

        vc.play(discord.FFmpegPCMAudio(filename, executable=FFMPEG_PATH))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 0.5

        while vc.is_playing() or vc.is_paused():
            await asyncio.sleep(1)

        if os.path.exists(filename):
            os.remove(filename)

        await self._process_queue(vc, guild)

    @discord.app_commands.command(name="skip", description="Skip the currently playing song.")
    async def skip(self, interaction: discord.Interaction):
        """Skips the currently playing song."""
        vc = interaction.guild.voice_client

        if not vc or not vc.is_playing():
            await interaction.response.send_message("❌ No song is currently playing!", ephemeral=True)
            return

        await interaction.response.defer()
        vc.stop()
        await interaction.followup.send("⏭ Skipping the current song!")

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
    await bot.add_cog(Music(bot))