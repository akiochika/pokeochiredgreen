import os
import random
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = discord.Object(id=123456789012345678)  # あなたのサーバーIDに置き換えてください

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=GUILD_ID)
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="gacha", description="1〜10の数字をランダムに出します", guild=GUILD_ID)
async def gacha_command(interaction: discord.Interaction):
    number = random.randint(1, 10)
    await interaction.response.send_message(f"🎲 あなたのガチャ結果は：**{number}** です！")

bot.run(TOKEN)
