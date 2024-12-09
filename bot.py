# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from config_loader import ConfigLoader
from chat_ai import ChatAI
from PIL import Image
from io import BytesIO

load_dotenv()

# ------------- 設定読み込み -------------
CONFIG_PATH = "config.yaml"
config = ConfigLoader(CONFIG_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# ------------- ChatAIインスタンス生成 -------------
chat_ai = ChatAI(
    api_key=GEMINI_API_KEY,
    model=config.gemini_model,
    system_prompt=config.system_prompt,
    error_message=config.error_message,
)

# ------------- Discord Bot部品準備 -------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix="!")  # prefixは任意


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    # 自分自身の発言は無視
    if message.author.bot:
        return

    # メンションまたはリプライをトリガーとする
    is_mentioned = bot.user.mentioned_in(message)
    is_reply_to_bot = (
        message.reference
        and message.reference.resolved
        and isinstance(message.reference.resolved, discord.Message)
        and message.reference.resolved.author == bot.user
    )

    if not (is_mentioned or is_reply_to_bot):
        return

    # チャンネル名フィルタ
    if message.channel.name not in config.allowed_channels:
        return

    # メンションテキストを除去
    content = message.content
    for user_mention in message.mentions:
        content = content.replace(user_mention.mention, "")
    content = content.strip()

    # ユーザー名取得(サーバー内のニックネームを優先)
    username = message.author.display_name

    # 添付ファイル処理(PILで読み込み)
    images = []
    for attachment in message.attachments:
        # ファイルをバイト列で取得
        file_bytes = await attachment.read()
        # PILで画像を開く
        try:
            img = Image.open(BytesIO(file_bytes))
            images.append(img)
        except Exception:
            pass  # 画像以外のファイルの場合等、必要に応じてエラーハンドリング

    # Reactionをつけて受付を示す
    try:
        await message.add_reaction(config.reaction_emoji)
    except Exception:
        pass

    # 入力中ステータス表示
    async with message.channel.typing():
        # AIへ問い合わせ
        status_code, ai_response = chat_ai.generate_response(
            user_content=content, user_name=username, images=images
        )

    # レスポンス処理
    if status_code == 200:
        await message.reply(ai_response, mention_author=True)
    else:
        await message.reply(ai_response, mention_author=True)


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
