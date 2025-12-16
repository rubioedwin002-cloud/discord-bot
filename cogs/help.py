import discord
from discord.ext import commands

# Role hierarchy (same as moderation.py so checks stay consistent)
ROLE_HIERARCHY = {
    "Owner": 4,
    "Co-Owner": 3,
    "Admin": 2,
    "Moderator": 1
}

def get_highest_rank(member: discord.Member):
    rank = 0
    for role in member.roles:
        if role.name in ROLE_HIERARCHY:
            rank = max(rank, ROLE_HIERARCHY[role.name])
    return rank

def require_role(min_rank):
    async def predicate(ctx):
        user_rank = get_highest_rank(ctx.author)
        if user_rank < min_rank:
            raise commands.CheckFailure("You don’t have the required role to use this command.")
        return True
    return commands.check(predicate)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="modhelp")
    @require_role(1)  # Moderator and above
    async def modhelp(self, ctx):
        # Delete the invoking message to keep channels clean
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass  # If bot can't delete, ignore

        # Build the help embed
        embed = discord.Embed(
            title="🛡️ Moderation Help",
            description="List of available moderation commands",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Moderator+",
            value=(
                "`!warn @user [reason]`\n"
                "`!warnings @user`\n"
                "`!mute @user [reason]`\n"
                "`!unmute @user`\n"
                "`!tempmute @user [seconds] [reason]`\n"
                "`!clear [amount]`\n"
                "`!purgeuser @user [amount]`\n"
                "`!userinfo @user`\n"
                "`!setmodlog #channel`"
            ),
            inline=False
        )

        embed.add_field(
            name="Admin+",
            value=(
                "`!kick @user [reason]`\n"
                "`!tempban @user [seconds] [reason]`"
            ),
            inline=False
        )

        embed.add_field(
            name="Co‑Owner+",
            value=(
                "`!ban @user [reason]`\n"
                "`!unban username`"
            ),
            inline=False
        )

        # Send privately to the user
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("⚠️ I couldn’t DM you the help menu. Please enable DMs from server members.", delete_after=5)

    # Shared error handler for role checks
    @modhelp.error
    async def modhelp_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(error), delete_after=5)

# Required async setup
async def setup(bot):
    await bot.add_cog(Help(bot))