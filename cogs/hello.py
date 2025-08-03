import os
import sys

class HelloCog:
    async def cmd_hello(self, ctx, args):
        user = ctx["user"]["name"]
        await ctx["reply"](f"こんにちは、{user} さん！")

    async def cmd_discord(self, ctx, args):
        await ctx["reply"](f"これが招待リンクです！\nhttps://discord.gg/mUyByHYMGk")

    async def cmd_restart(self, ctx, args):
        print(f'Restart実行者: {ctx["user"]["id"]}')
        if ctx["owner"] != ctx["user"]["id"]:
            return
        await ctx["close"]()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    async def cmd_userid(self, ctx, args):
        await ctx["reply"](f"あなたのユーザーid: {ctx["user"]["id"]}")

    async def cmd_help(self, ctx, args):
        await ctx["reply"](f"""私ができること:
/help .. ヘルプを見ます！
/hello .. 挨拶をします！
/test .. 正常に動作しているかテストします。
/discord .. 私を開発しているDiscordサーバーに参加します。
/userid .. ユーザーidを取得します。

コマンドを使う際には必ず「メンション /コマンド名」と入力してね！""")