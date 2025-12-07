import os
import re
from telethon import TelegramClient
from quart import Quart, request, Response

# ==============================
# 👇 ခင်ဗျား Info တွေ ပြန်ဖြည့်ပါ
# ==============================
API_ID = 33303007  # <--- ပြန်ဖြည့်ပါ
API_HASH = "0b2d5c12581981592d9f86fec689289c"  # <--- ပြန်ဖြည့်ပါ
BOT_TOKEN = "8553199381:AAF-vbWyca24HsYDK8qwHewnhkW34Uxta1k"  # <--- ပြန်ဖြည့်ပါ
CHANNEL_ID = -1002395717312 # <--- ပြန်ဖြည့်ပါ
# ==============================

app = Quart(__name__)
client = TelegramClient('bot_session', API_ID, API_HASH)

@app.before_serving
async def startup():
    await client.start(bot_token=BOT_TOKEN)

@app.route('/')
async def hello():
    return "🚀 Advanced Streamer is Running!"

@app.route('/video/<int:msg_id>')
async def stream_video(msg_id):
    try:
        # Message ကို အရင်ဆွဲထုတ်မယ် (File Info လိုချင်လို့)
        message = await client.get_messages(CHANNEL_ID, ids=msg_id)
        
        if not message or not message.media:
            return "Video not found", 404

        file_size = message.file.size
        file_name = message.file.name or f"video_{msg_id}.mp4"
        mime_type = message.file.mime_type or "video/mp4"

        # Browser က Range (ကျော်ကြည့်ဖို့) တောင်းလာလား စစ်မယ်
        range_header = request.headers.get('Range')
        
        # Default အနေအထား (အစအဆုံး)
        start, end = 0, file_size - 1
        status_code = 200

        # Range ပါလာရင် တွက်ချက်မယ်
        if range_header:
            byte1, byte2 = 0, None
            match = re.search(r'(\d+)-(\d*)', range_header)
            groups = match.groups()

            if groups[0]: byte1 = int(groups[0])
            if groups[1]: byte2 = int(groups[1])

            start = byte1
            if byte2: end = byte2
            
            status_code = 206 # Partial Content (အကျိုးအပဲ့ ပို့ခြင်း)

        chunk_size = end - start + 1

        # Headers တွေ သေချာပြန်ပို့မယ် (ဒါမှ Browser က ကျော်လို့ရမှန်း သိမှာ)
        headers = {
            'Content-Type': mime_type,
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_size),
            'Content-Disposition': f'inline; filename="{file_name}"'
        }

        # Telegram ဆီကနေ လိုချင်တဲ့အပိုင်း (Offset) ကိုပဲ တောင်းပြီး ပြန်ပို့မယ်
        async def generate():
            async for chunk in client.iter_download(
                message.media, 
                offset=start, 
                limit=chunk_size, 
                chunk_size=1024*1024 # 1MB chunks (ပိုမြန်အောင်)
            ):
                yield chunk

        return Response(generate(), status=status_code, headers=headers)

    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
