import discord
from discord.ext import commands
import json
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

GACHA_COST = 500
USERS_FILE = "users.json"
ITEMS_FILE = "gacha_items.json"
IMAGE_FOLDER = "images"

RARITY_COLORS = {
    "SSR": discord.Color.gold(),
    "SR": discord.Color.purple(),
    "R": discord.Color.blue(),
    "N": discord.Color.gray()
}

RARITY_EMOJIS = {
    "SSR": "🌟",
    "SR": "✨",
    "R": "🔹",
    "N": "🔸"
}

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def choose_random_item():
    items = load_json(ITEMS_FILE)
    item_ids = list(items.keys())
    weights = [items[i]["rate"] for i in item_ids]
    chosen_id = random.choices(item_ids, weights=weights, k=1)[0]
    return chosen_id, items[chosen_id]

def ensure_user(user_id):
    users = load_json(USERS_FILE)
    if str(user_id) not in users:
        users[str(user_id)] = {"points": 1000, "collection": []}
        save_json(USERS_FILE, users)
    return users

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user.name}')

@bot.command()
async def start(ctx):
    users = load_json(USERS_FILE)
    user_id = str(ctx.author.id)
    if user_id in users:
        await ctx.send("すでに登録済みです！")
    else:
        users[user_id] = {"points": 1000, "collection": []}
        save_json(USERS_FILE, users)
        await ctx.send("ゲームスタート！1000ポイントを付与しました！")

@bot.command()
async def gacha(ctx):
    users = ensure_user(ctx.author.id)
    user = users[str(ctx.author.id)]

    if user["points"] < GACHA_COST:
        await ctx.send("ポイントが足りません！（500ポイント必要）")
        return

    user["points"] -= GACHA_COST
    item_id, item = choose_random_item()
    user["collection"].append(item_id)
    save_json(USERS_FILE, users)

    rarity = item.get("rarity", "N")
    emoji = RARITY_EMOJIS.get(rarity, "")
    color = RARITY_COLORS.get(rarity, discord.Color.light_gray())

    file_path = os.path.join(IMAGE_FOLDER, item["filename"])
    with open(file_path, 'rb') as f:
        file = discord.File(f, filename=item["filename"])
        embed = discord.Embed(
            title=f"{emoji} {item['name']} をゲット！",
            color=color
        )
        embed.set_image(url=f"attachment://{item['filename']}")
        embed.set_footer(text=f"レアリティ: {rarity}")
        await ctx.send(embed=embed, file=file)

@bot.command()
async def points(ctx):
    users = ensure_user(ctx.author.id)
    point = users[str(ctx.author.id)]["points"]
    await ctx.send(f"あなたの所持ポイント：{point}pt")

@bot.command()
async def collection(ctx):
    users = ensure_user(ctx.author.id)
    user = users[str(ctx.author.id)]
    items = load_json(ITEMS_FILE)

    if not user["collection"]:
        await ctx.send("まだ何もコレクションしていません。")
        return

    msg = "📦 あなたのコレクション:\n"
    count = {}
    for item_id in user["collection"]:
        count[item_id] = count.get(item_id, 0) + 1

    for item_id, c in count.items():
        name = items[item_id]["name"]
        rarity = items[item_id].get("rarity", "N")
        emoji = RARITY_EMOJIS.get(rarity, "")
        msg += f"- {emoji} {name} × {c}\n"

    await ctx.send(msg)

@bot.command()
@commands.has_permissions(administrator=True)
async def give(ctx, member: discord.Member, amount: int):
    users = ensure_user(member.id)
    users[str(member.id)]["points"] += amount
    save_json(USERS_FILE, users)
    await ctx.send(f"{member.mention} に {amount} ポイントを付与しました。")

# Railway用：環境変数 TOKEN からトークン取得
bot.run(os.getenv("TOKEN"))
