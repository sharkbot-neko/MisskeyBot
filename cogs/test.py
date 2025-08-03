class TestCog:
    async def cmd_test(self, ctx, args):
        await ctx["reply"](f"私は正常に動作しています！")