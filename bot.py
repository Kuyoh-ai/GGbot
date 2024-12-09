import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from config_loader import ConfigLoader
from chat_ai import ChatAI
import base64

load_dotenv()

# ------------- 設定読み込み -------------
CONFIG_PATH = "config.yaml"
config = ConfigLoader(CONFIG_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# ------------- クラス分離: ChatAIインスタンス生成 -------------
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

bot = commands.Bot(intents=intents, command_prefix="!")  # prefixは適宜


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    # 自分自身の発言は無視
    if message.author.bot:
        return

    # メンションまたはリプライをトリガーとする
    # メンション判定
    is_mentioned = bot.user.mentioned_in(message)
    # リプライ判定
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

    # メンションテキスト除去
    # メンション部分を削除してユーザー発言のみ抽出
    content = message.content
    for user_mention in message.mentions:
        content = content.replace(user_mention.mention, "")
    content = content.strip()

    # ユーザー名取得(サーバー内のニックネームを優先)
    username = message.author.display_name

    # 添付ファイル処理(base64)
    attachments_data = []
    for attachment in message.attachments:
        # ファイルをバイト列で取得
        file_bytes = await attachment.read()
        # base64エンコード
        encoded = base64.b64encode(file_bytes)
        attachments_data.append(encoded)

    # Reactionをつけて受付を示す
    try:
        await message.add_reaction(config.reaction_emoji)
    except Exception:
        pass

    # 入力中ステータス表示
    async with message.channel.typing():
        # AIへ問い合わせ
        status_code, ai_response = chat_ai.generate_response(
            user_content=content, attachments=attachments_data
        )

    # レスポンス処理
    if status_code == 200:
        # メンションまたはリプライ元ユーザーに返信
        # リプライで返信 (スレッドやDMなどの要件によって変更)
        await message.reply(ai_response, mention_author=True)
    else:
        await message.reply(ai_response, mention_author=True)


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
