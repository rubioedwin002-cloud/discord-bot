import discord
from discord.ext import commands
import asyncio

# Role hierarchy
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

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}  # {user_id: [reasons]}
        self.modlog_channel = None

    # --- Utility: set modlog channel ---
    @commands.command()
    @require_role(1)
    async def setmodlog(self, ctx, channel: discord.TextChannel):
        self.modlog_channel = channel
        await ctx.send(f"✅ Mod log channel set to {channel.mention}")

    async def log_action(self, ctx, action: str):
        if self.modlog_channel:
            await self.modlog_channel.send(f"📋 **{action}** by {ctx.author.mention} in {ctx.channel.mention}")

    # --- Warn system ---
    @commands.command()
    @require_role(1)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        self.warnings.setdefault(member.id, []).append(reason or "No reason provided")
        await ctx.send(f"⚠️ {member.mention} has been warned. Reason: {reason}")
        await self.log_action(ctx, f"Warned {member} ({reason})")

    @commands.command()
    @require_role(1)
    async def warnings(self, ctx, member: discord.Member):
        user_warnings = self.warnings.get(member.id, [])
        if not user_warnings:
            await ctx.send(f"{member.mention} has no warnings.")
        else:
            await ctx.send(f"{member.mention} has {len(user_warnings)} warnings:\n- " + "\n- ".join(user_warnings))

    # --- Temp mute ---
    @commands.command()
    @require_role(1)
    async def tempmute(self, ctx, member: discord.Member, duration: int, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"🔇 {member.mention} has been muted for {duration} seconds. Reason: {reason}")
        await self.log_action(ctx, f"Temporarily muted {member} ({reason})")

        await asyncio.sleep(duration)
        await member.remove_roles(muted_role)
        await ctx.send(f"🔊 {member.mention} has been automatically unmuted.")

    # --- Temp ban ---
    @commands.command()
    @require_role(2)
    async def tempban(self, ctx, member: discord.Member, duration: int, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"⛔ {member} has been banned for {duration} seconds. Reason: {reason}")
        await self.log_action(ctx, f"Temporarily banned {member} ({reason})")

        await asyncio.sleep(duration)
        await ctx.guild.unban(member)
        await ctx.send(f"✅ {member} has been automatically unbanned.")

    # --- Purge user (delete one by one) ---
    @commands.command()
    @require_role(1)
    async def purgeuser(self, ctx, member: discord.Member, amount: int = 100):
        """Delete messages from a specific user one by one."""
        deleted = 0
        async for message in ctx.channel.history(limit=amount):
            if message.author == member:
                try:
                    await message.delete()
                    deleted += 1
                except discord.Forbidden:
                    await ctx.send("⚠️ I don’t have permission to delete some messages.", delete_after=5)
                    break
                except discord.HTTPException:
                    await ctx.send("⚠️ Couldn’t delete a message (maybe too old).", delete_after=5)
                    break

        await ctx.send(f"🧹 Deleted {deleted} messages from {member.mention}.", delete_after=5)
        await self.log_action(ctx, f"Purged {deleted} messages from {member}")

    # --- User info ---
    @commands.command()
    @require_role(1)
    async def userinfo(self, ctx, member: discord.Member):
        embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=False)
        embed.add_field(name="Roles", value=", ".join([r.name for r in member.roles if r.name != "@everyone"]), inline=False)
        await ctx.send(embed=embed)

    # --- Old commands with hierarchy ---
    @commands.command()
    @require_role(2)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"{member} has been kicked. Reason: {reason}")
        await self.log_action(ctx, f"Kicked {member} ({reason})")

    @commands.command()
    @require_role(3)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"{member} has been banned. Reason: {reason}")
        await self.log_action(ctx, f"Banned {member} ({reason})")

    @commands.command()
    @require_role(3)
    async def unban(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member_name:
                await ctx.guild.unban(user)
                await ctx.send(f"✅ {user.name} has been unbanned.")
                await self.log_action(ctx, f"Unbanned {user}")
                return
        await ctx.send(f"⚠️ No banned user named {member_name} found.")

    @commands.command()
    @require_role(1)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"{member.mention} has been muted. Reason: {reason}")
        await self.log_action(ctx, f"Muted {member} ({reason})")

    @commands.command()
    @require_role(1)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted.")
            await self.log_action(ctx, f"Unmuted {member}")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.command()
    @require_role(1)
    async def clear(self, ctx, amount: int):
        await ctx.message.delete()
        count = 0
        async for message in ctx.channel.history(limit=amount):
            try:
                await message.delete()
                count += 1
            except discord.Forbidden:
                await ctx.send("⚠️ I don’t have permission to delete some messages.", delete_after=5)
                break
            except discord.HTTPException:
                await ctx.send("⚠️ Couldn’t delete a message (maybe too old).", delete_after=5)
                break
        await ctx.send(f"🧹 Cleared {count} messages.", delete_after=5)
        await self.log_action(ctx, f"Cleared {count} messages")

    # --- Shared error handler ---
    @warn.error
    @warnings.error
    @tempmute.error
    @tempban.error
    @purgeuser.error
    @userinfo.error
    @kick.error
    @ban.error
    @unban.error
    @mute.error
    @unmute.error
    @clear.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(str(error), delete_after=5)

# Required async setup
async def setup(bot):
    await bot.add_cog(Moderation(bot))