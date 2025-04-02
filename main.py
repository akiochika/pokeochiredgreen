import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = False  # スラッシュコマンドだけなら不要

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ ログインしました：{bot.user}")

@bot.tree.command(name="tokumei", description="匿名でメッセージを送信します")
async def tokumei(interaction: discord.Interaction, message: str):
    # ユーザー側には一時的な表示だけ（他人には見えない）
    await interaction.response.send_message("匿名メッセージを送信しました ✅", ephemeral=True)
    # 実際のメッセージをBotが送信
    await interaction.channel.send(message)

# Botトークンを入れて実行
bot.run("YOUR_BOT_TOKEN")
