import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import ai

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(""), intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")

    try:
        bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ Slash commands synced successfully!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == CHANNEL_ID:
        response = ai.generate_response(message.content)
        await message.channel.send(response)
    await bot.process_commands(message)

async def load_extensions():
    """Loads all command files (cogs)."""
    try:
        await bot.load_extension("bot_commands")
        print("✅ Loaded bot_commands successfully!")
    except Exception as e:
        print(f"❌ Error loading bot_commands: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
