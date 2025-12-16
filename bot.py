import discord
from discord.ext import commands
import asyncio

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
async def main():
    async with bot:
        # Load your cogs here
        await bot.load_extension("cogs.moderation")
        await bot.load_extension("cogs.roles")
        await bot.load_extension("cogs.help")
        # Start the bot
        await bot.start("DISCORD_BOT_TOKEN")

# --- Run the bot ---
asyncio.run(main())