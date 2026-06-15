import discord
from discord.ext import commands

server_id = 1279409253983064117
GUILD_ID = discord.Object(server_id)

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="hello", description="Say Hello!")
    @discord.app_commands.guilds(GUILD_ID)
    async def sayHello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hi There!")

    @discord.app_commands.command(name="printer", description="I Will Print What Ever You Send to Me!")
    @discord.app_commands.guilds(GUILD_ID)
    async def printer(self, interaction: discord.Interaction, printer: str):
        await interaction.response.send_message(printer)

    @discord.app_commands.command(name="bot_profile", description="See Bot Profile")
    @discord.app_commands.guilds(GUILD_ID)
    async def show_bot_profile(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="I am Cytus Assistant",
            description="Running Slash Commands - Bot on Development",
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(
            url="https://upload.wikimedia.org/wikipedia/id/c/c6/Sasuke_Uchiha_%28Good%2CShippuden%29.jpg"
        )
        embed.add_field(name="Fishing Games", value="Type /fish to Start", inline=False)
        embed.add_field(name="Mining Games", value="Type /mine to Start")
        embed.set_footer(text="Developed By Cytus#9999")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Misc(bot))
