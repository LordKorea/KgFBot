from misc.adapter import create_bot, connect_bot
from bot import Bot

if __name__ == "__main__":
    rf = Bot()
    bot = create_bot(rf, rf.config.get("cmd-prefix", "."))
    rf.bot = bot
    connect_bot(bot)
