import discord
from misc.util import init_logging, log


def create_bot(piggyback, cmdprefix="."):
    """Create a bot and setup logging.

    Args:
        piggyback: The piggyback object.
    """
    init_logging()
    bot = discord.Client()
    bot.data = piggyback

    @bot.event
    async def on_ready():
        log("=================================================================")
        log("Logged in as {0.user.name} with ID {0.user.id}".format(bot))
        log("=================================================================")
        await bot.data.on_ready()

    @bot.event
    async def on_message_delete(message):
        await bot.data.on_message_delete(message)

    @bot.event
    async def on_message_edit(before, after):
        await bot.data.on_message_edit(before, after)

    @bot.event
    async def on_member_join(member):
        await bot.data.on_member_join(member)

    @bot.event
    async def on_member_remove(member):
        await bot.data.on_member_remove(member)

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        await bot.data.on_message(message)

        if message.content.startswith(cmdprefix):
            command = message.content[1:]
            parts = command.split(" ")

            if len(parts) < 1:
                return

            log("Got '{0}' from {1.author}".format(command, message))
            await bot.data.handle_command(message, parts[0], parts[1:])

    return bot


def connect_bot(bot):
    """Connects a bot via the authentication token.

    Args:
        bot: The bot.
    """
    try:
        with open("tokenfile", "r") as tokenfile:
            token = tokenfile.read().strip()
        bot.run(token)
    except FileNotFoundError:
        print("Could not find 'tokenfile', aborting.")
