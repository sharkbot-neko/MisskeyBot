import asyncio
import json
import aiohttp
from misskey import Misskey
from dotenv import load_dotenv
import os
import importlib

from bot import CommandBot
import cogs.hello
import cogs.test

load_dotenv()
TOKEN = os.environ["TOKEN"]
OWNER = os.environ["OWNER"]

print(f"オーナーid: {OWNER}")

INSTANCE = "misskey.io"

msk = Misskey(INSTANCE, i=TOKEN)
MY_ID = msk.i()["id"]

bot = CommandBot()
bot.load_cog("hello", cogs.hello.HelloCog)
bot.load_cog("test", cogs.test.TestCog)

async def post_note(reply_to, text):
    msk.notes_create(text=text, reply_id=reply_to)

async def runner():
    ws_url = f"wss://{INSTANCE}/streaming?i={TOKEN}"
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ws_url) as ws:
                    await ws.send_json({
                        "type": "connect",
                        "body": {
                            "channel": "main",
                            "id": "mention-stream"
                        }
                    })
                    print(f"✅ 接続完了: {MY_ID}")

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if data.get("type") == "channel" and data["body"].get("type") == "mention":
                                note = data["body"]["body"]
                                user_id = note["user"]["id"]
                                if user_id == MY_ID:
                                    continue

                                async def reply(text):
                                    await post_note(reply_to=note["id"], text=text)

                                async def close():
                                    await ws.close()
                                    return

                                ctx = {
                                    "text": note.get("text", "").removeprefix("@sharkbot_misskey").removeprefix(" "),
                                    "user": note["user"],
                                    "reply": reply,
                                    "owner": OWNER,
                                    "close": close,
                                }

                                await bot.handle(ctx)
        except Exception as e:
            print("⚠️ 接続エラー:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(runner())