import discord
from discord.ext import commands
from database import get_user_profile, get_money

server_id = 1279409253983064117
GUILD_ID = discord.Object(server_id)

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="profile", description="View your fishing profile")
    @discord.app_commands.guilds(GUILD_ID)
    async def profile(self, interaction: discord.Interaction):
        profile = get_user_profile(interaction.user.id)

        if not profile:
            await interaction.response.send_message(
                "❌ Profile not found. Try fishing first with `/fish`.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎣 Fishing Profile",
            color=discord.Color.blurple()
        )

        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar.url
        )

        embed.add_field(name="💰 Money", value=f"{profile['money']} coins", inline=True)
        embed.add_field(name="🎯 Rod Level", value=f"Level {profile['rod_level']}", inline=True)
        embed.add_field(name="🐟 Total Fish Caught", value=profile["total_fish"], inline=False)
        embed.add_field(name="📦 Inventory Value", value=f"{profile['inventory_value']} coins", inline=False)

        embed.set_footer(text="Upgrade your rod to catch rarer fish")

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="balance", description="Check your balance")
    @discord.app_commands.guilds(GUILD_ID)
    async def balance(self, interaction: discord.Interaction):
        money = get_money(interaction.user.id)

        embed = discord.Embed(title="💰 Balance", color=discord.Color.gold())
        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar.url
        )
        embed.add_field(name="Coins", value=f"{money} coins", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
