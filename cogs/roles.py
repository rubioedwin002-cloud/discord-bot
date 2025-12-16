import discord
from discord.ext import commands

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

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addrole(self, ctx, member: discord.Member, role_name: str):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            return await ctx.send(f"⚠️ Role '{role_name}' does not exist.")

        giver_rank = get_highest_rank(ctx.author)
        target_rank = ROLE_HIERARCHY.get(role_name, 0)

        if member == ctx.author and giver_rank <= target_rank:
            return await ctx.send("⚠️ You cannot give yourself a role of equal or higher authority.")
        if giver_rank <= target_rank:
            return await ctx.send(f"⚠️ You need a higher role than '{role_name}' to assign it.")

        await member.add_roles(role)
        await ctx.send(f"✅ {member.mention} has been given the '{role_name}' role.")

    @commands.command()
    async def removerole(self, ctx, member: discord.Member, role_name: str):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            return await ctx.send(f"⚠️ Role '{role_name}' does not exist.")

        giver_rank = get_highest_rank(ctx.author)
        target_rank = ROLE_HIERARCHY.get(role_name, 0)

        if giver_rank <= target_rank:
            return await ctx.send(f"⚠️ You cannot remove a role equal or higher than your own.")

        await member.remove_roles(role)
        await ctx.send(f"✅ {role_name} role removed from {member.mention}.")

    @commands.command()
    async def createrole(self, ctx, role_name: str):
        if role_name not in ROLE_HIERARCHY:
            return await ctx.send("⚠️ Only roles in the hierarchy can be created this way.")

        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.send(f"⚠️ Role '{role_name}' already exists.")
        else:
            await ctx.guild.create_role(name=role_name)
            await ctx.send(f"✅ Role '{role_name}' has been created.")

# Required async setup
async def setup(bot):
    await bot.add_cog(Roles(bot))