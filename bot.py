import discord
from discord.ext import commands
import asyncio
import os

# --- Intents ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# --- Bot Setup ---
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Events ---
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

# --- Owner-only reload command ---
@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"🔄 Reloaded {extension} cog successfully!")
    except Exception as e:
        await ctx.send(f"⚠️ Failed to reload {extension}: {e}")

# --- Async startup to load cogs ---
async def start_bot():
    async with bot:
        # Load or reload cogs safely
        for ext in ["cogs.moderation", "cogs.roles", "cogs.help"]:
            if ext in bot.extensions:
                await bot.reload_extension(ext)
                print(f"🔄 Reloaded {ext}")
            else:
                await bot.load_extension(ext)
                print(f"✅ Loaded {ext}")

        # Get token from environment variable
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise RuntimeError("❌ DISCORD_TOKEN environment variable not set!")

        # Start the bot
        await bot.start(token)

# --- Run the bot indefinitely ---
while True:
    try:
        asyncio.run(start_bot())
    except Exception as e:
        print(f"⚠️ Bot crashed with error: {e}. Restarting...")
        continue