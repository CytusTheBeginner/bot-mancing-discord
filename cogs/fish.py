import time
import discord
from discord.ext import commands
from discord import app_commands
from database import (
    get_user,
    create_user,
    get_inventory,
    get_fish_by_name,
    add_fish_to_inventory,
    sell_by_rarity
)
from fish_logic import fish_roll

RARITIES = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]

server_id = 1279409253983064117
GUILD_ID = discord.Object(server_id)

class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        
    @discord.app_commands.command(name="fish", description="Go fishing!")
    @discord.app_commands.guilds(GUILD_ID)
    async def fish(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = time.time()

        cooldown = 8
        last_used = self.cooldowns.get(user_id, 0)
        
        if now - last_used < cooldown:
            remaining = int(cooldown - (now - last_used))
            await interaction.response.send_message(
                f"⏳ Slow down! Try again in **{remaining}s**.",
                ephemeral=True
            )
            return

        self.cooldowns[user_id] = now
        
        await interaction.response.defer() 

        user = get_user(user_id)
        if not user:
            create_user(user_id)
            user = get_user(user_id)

        result = fish_roll(user["rod_level"])

        if result is None:
            await interaction.response.send_message("🎣 You got nothing...")
            return

        add_fish_to_inventory(user_id, result["id"])

        embed = discord.Embed(
            title="🎣 Fishing Result",
            description=f"You have caught **{result['name']}**!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=result["image_url"])
        embed.add_field(name="Sell Price", value=f"{result['price']} coins")

        await interaction.followup.send(embed=embed)

    @discord.app_commands.command(name="inventory", description="View your fishing inventory")
    @discord.app_commands.guilds(GUILD_ID)
    async def inventory(self, interaction: discord.Interaction):
        items = get_inventory(interaction.user.id)

        if not items:
            await interaction.response.send_message(
                "🎣 Your inventory is empty.\nGo fishing first with `/fish`.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🎣 {interaction.user.name}'s Inventory",
            color=discord.Color.blue()
        )

        total_value = 0
        for item in items:
            subtotal = item["price"] * item["amount"]
            total_value += subtotal

            embed.add_field(
                name=f"{item['name']} x{item['amount']}",
                value=f"💰 Value: {subtotal} coins",
                inline=False
            )

        embed.set_footer(text=f"Total Inventory Value: {total_value} coins")
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="view", description="View a fish image and details")
    @discord.app_commands.guilds(GUILD_ID)
    async def view(self, interaction: discord.Interaction, fish_name: str):
        fish = get_fish_by_name(fish_name)

        if not fish:
            await interaction.response.send_message(
                f"❌ Fish **{fish_name}** not found.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🐟 {fish['name']}",
            color=discord.Color.gold()
        )
        embed.set_image(url=fish["image_url"])
        embed.add_field(name="Chance", value=f"{fish['chance']}%", inline=True)
        embed.add_field(name="Sell Price", value=f"{fish['price']} coins", inline=True)

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="sell", description="Sell fishes by rarity")
    @app_commands.describe(rarity="Fish rarity to sell")
    @discord.app_commands.guilds(GUILD_ID)
    async def sell(self, interaction: discord.Interaction, rarity: str):
        rarity = rarity.upper()

        if rarity not in RARITIES:
            await interaction.response.send_message(
                f"❌ Invalid rarity.\nChoose: {', '.join(RARITIES)}",
                ephemeral=True
            )
            return

        earned = sell_by_rarity(interaction.user.id, rarity)

        if earned == 0:
            await interaction.response.send_message(
                f"🎒 You have no **{rarity}** fish to sell.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="💰 Fish Sold",
            description=f"You sold all **{rarity}** fish.",
            color=discord.Color.green()
        )
        embed.add_field(name="Earned", value=f"{earned} coins")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fishing(bot))
