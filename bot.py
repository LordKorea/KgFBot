from misc.adapter import log
from misc.config import Config
import discord


class Bot:

    def __init__(self):
        self.bot = None
        self.modules = []
        self.config = Config()

    async def on_ready(self):
        """Event handler for when the bot is ready."""
        log("Initializing bot presence...")
        game = self.config.get("game-presence", "Skynet")
        await self.bot.change_presence(activity=discord.Game(name=game))

        log("Loading modules...")
        self.modules = [
            # Add modules here...
        ]

        log("Initialization complete, %d modules loaded." % len(self.modules))

    async def on_message_delete(self, msg):
        """Event handler for when a message is deleted.

        Args:
            msg: The message that was deleted.
        """
        for module in self.modules:
            await module.on_message_delete(msg)

    async def on_message_edit(self, before, after):
        """Event handler for when a message is edited.

        Args:
            before: The message before the edit.
            after: The message after the edit.
        """
        for module in self.modules:
            await module.on_message_edit(before, after)

    async def on_member_join(self, member):
        """Event handler for when a member joins the server.

        Args:
            member: The member that joined the server.
        """
        for module in self.modules:
            await module.on_member_join(member)

    async def on_member_remove(self, member):
        """Event handler for when a member leaves the server.

        Args:
            member: The member that left the server.
        """
        for module in self.modules:
            await module.on_member_remove(member)

    async def on_message(self, msg):
        """Event handler for messages.

        Args:
            msg: The message.
        """
        for module in self.modules:
            await module.on_message(msg)

    async def handle_command(self, msg, cmd, args):
        """Event handler for commands.

        Args:
            msg: The message that contains the command.
            cmd: The command.
            args: The arguments provided.
        """
        for module in self.modules:
            await module.on_command(msg, cmd, args)
