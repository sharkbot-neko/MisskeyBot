import time
import importlib
import sys

class CommandBot:
    def __init__(self):
        self.commands = {}
        self.cooldowns = {}  # {(user_id, command): last_called}
        self.cooldown_seconds = {}  # {command: 秒数}
        self.cogs = {}

    def command(self, name, cooldown=0):
        def decorator(func):
            self.commands[name] = func
            if cooldown > 0:
                self.cooldown_seconds[name] = cooldown
            return func
        return decorator

    def load_cog(self, name, module):
        cog = module()
        self.cogs[name] = module  # 保存しておく
        for attr in dir(cog):
            if attr.startswith("cmd_"):
                cmd_name = "/" + attr[4:]
                self.commands[cmd_name] = getattr(cog, attr)

    def reload_cog(self, name):
        if name not in self.cogs:
            return False, "Cog not found."
        try:
            modname = self.cogs[name].__module__
            newmod = importlib.reload(sys.modules[modname])
            self.load_cog(name, getattr(newmod, name))
            return True, f"Reloaded cog '{name}'"
        except Exception as e:
            return False, str(e)

    async def handle(self, ctx):
        content = ctx["text"]
        if not content.startswith("/"):
            return

        parts = content.split()
        cmd = parts[0]
        args = parts[1:]
        user_id = ctx["user"]["id"]

        cooldown = self.cooldown_seconds.get(cmd)
        if cooldown:
            key = (user_id, cmd)
            last = self.cooldowns.get(key, 0)
            now = time.time()
            if now - last < cooldown:
                remain = round(cooldown - (now - last), 1)
                return
            self.cooldowns[key] = now

        handler = self.commands.get(cmd)
        if handler:
            await handler(ctx, args)
