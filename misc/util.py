import discord
import logging
from datetime import datetime


def dateformat(dtime=None):
    """Formats a date.

    Args:
        dtime: The datetime. If None, this will be the current time.
    """
    if dtime is None:
        dtime = datetime.now()
    return dtime.strftime("%Y-%m-%d %H:%M:%S")


def init_logging():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8",
                                  mode="w")
    formatter = logging.Formatter("[%(asctime)s:%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log(msg):
    """Logs a message.

    Args:
        msg: The message.
    """
    logger = logging.getLogger("discord")
    logger.info(msg)
    print(msg)


def create_embed(title, text, color, data=None):
    """Creates an embed.

    Args:
        title: The title for the embed.
        text: The text for the embed.
        color: The color of the embed.
        data: Data entries for the embed.
    Returns:
        The created embed.
    """
    if data is None:
        data = {}
    embed = discord.Embed(title=title, description=text, color=color)
    for key in data:
        embed.add_field(name=key, value=data[key])
    return embed
