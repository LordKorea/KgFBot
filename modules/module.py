from discord import ChannelType
from misc.util import log


class Module:

    def __init__(self, frontend, bot):
        """Constructor."""
        self._frontend = frontend
        self._bot = bot

    async def on_message(self, msg):
        """Event handler for messages.

        Args:
            msg: The message.
        """
        pass

    async def on_message_delete(self, msg):
        """Event handler for message deletion.

        Args:
            msg: The message.
        """
        pass

    async def on_message_edit(self, msg, msgnew):
        """Event handler for message editing.

        Args:
            msg: The old message.
            msgnew: The new message.
        """
        pass

    async def on_member_join(self, member):
        """Event handler for member join.

        Args:
            member: The member.
        """
        pass

    async def on_member_remove(self, member):
        """Event handler for member removal.

        Args:
            member: The member.
        """
        pass

    async def on_command(self, msg, cmd, args):
        """Event handler for commands.

        Args:
            msg: The message.
            cmd: The command label.
            args: The command arguments.
        """
        pass
