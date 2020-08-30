import os

from core.discord_bot import DiscordBot

from core.db_tools import update_db

def main():
    bot = DiscordBot("Extensible bot based on Discord.py's Cogs")

    @bot.event
    async def on_ready():
        # If this is the first launch (Not a reconnection from disconnect)
        if bot.first_launch:
            # Load core modules first
            bot.load_extension("core.plugins.core")
            bot.load_extension("core.plugins.plugin_manager")

            # Followed by available plugins
            for p in sorted(os.listdir("plugins")):
                if not p.endswith(".py"):
                    continue

                plugin = p.split(".")[0]

                if plugin == "__pycache__":
                    return

                try:
                    bot.load_extension(f"plugins.{plugin}")
                    bot.plugins.append(plugin)
                    update_db(bot.db, bot.plugins, "plugins")
                except Exception as e:
                    exc = "{0}: {1}".format(type(e).__name__, e)
                    bot.log.warning(f"Failed to load plugin {p}:\n    - {exc}")

            bot.app_info = await bot.application_info()

            bot.first_launch = False

        bot.log.info("\n".join(bot.mission_control()))

        # Ensure all currently joined severs are registered
        for server in bot.guilds:
            sid = str(server.id)
            if sid not in bot.servers:
                bot.servers[sid] = {}

        update_db(bot.db, bot.servers, "servers")

    bot.run(bot.config_token)

if __name__ == "__main__":
    main()
