import os
import logging
import discord
from discord.ext import commands
from keep_alive import keep_alive  # Only needed if hosting on Replit

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("bot")

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
    log.info(f"✅ Bot is online as {bot.user} (ID: {bot.user.id})")

# --- Owner-only reload command ---
@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"🔄 Reloaded {extension} cog successfully!")
    except Exception as e:
        await ctx.send(f"⚠️ Failed to reload {extension}: {e}")

# --- Cog loading before bot starts ---
@bot.event
async def setup_hook():
    for ext in ["cogs.moderation", "cogs.roles", "cogs.help"]:
        try:
            if ext in bot.extensions:
                await bot.reload_extension(ext)
                log.info(f"Reloaded {ext}")
            else:
                await bot.load_extension(ext)
                log.info(f"Loaded {ext}")
        except Exception as e:
            log.error(f"Failed to load {ext}: {e}")

def main():
    # Keep-alive server (Replit only)
    try:
        keep_alive()
    except ImportError:
        log.info("No keep_alive module found — skipping.")

    # Get token from environment variable
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_TOKEN environment variable not set!")

    bot.run(token)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception(f"Bot failed to start: {e}")