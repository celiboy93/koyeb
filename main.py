import os
from telethon import TelegramClient
from quart import Quart, request, Response

# ==============================
# 👇 ဒီနေရာမှာ ခင်ဗျား Info တွေ ဖြည့်ပါ
# ==============================
API_ID = 33303007
API_HASH = "0b2d5c12581981592d9f86fec689289c"
BOT_TOKEN = "8553199381:AAF-vbWyca24HsYDK8qwHewnhkW34Uxta1k"
CHANNEL_ID = -1002395717312 # Channel ID (Bot ကို Admin ပေးထားရမယ်)
# ==============================

app = Quart(__name__)
client = TelegramClient('bot_session', API_ID, API_HASH)

@app.before_serving
async def startup():
    await client.start(bot_token=BOT_TOKEN)

@app.route('/')
async def hello():
    return "Streamer Bot is Running!"

@app.route('/video/<int:msg_id>')
async def stream_video(msg_id):
    try:
        # Telegram ကနေ ဖိုင်ကို တိုက်ရိုက် Stream မယ်
        message = await client.get_messages(CHANNEL_ID, ids=msg_id)
        
        if not message or not message.media:
            return "Video not found", 404

        # Browser ကို Video ပါလို့ ပြောမယ်
        headers = {
            'Content-Type': message.file.mime_type,
            'Content-Disposition': f'inline; filename="{message.file.name or "video.mp4"}"'
        }

        # IterChunk နဲ့ တိုက်ရိုက် Stream ခြင်း (Download မဆွဲဘဲ ပြမယ်)
        async def generate():
            async for chunk in client.iter_download(message.media):
                yield chunk

        return Response(generate(), headers=headers)

    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
