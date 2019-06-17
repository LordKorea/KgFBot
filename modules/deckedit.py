import asyncio
from json import load, dump
from misc.util import create_embed, log
from model.deck import Deck
from modules.module import Module
from os.path import exists


class DeckEditModule(Module):

    def __init__(self, frontend, bot):
        """Constructor.

        Args:
            frontend: The bot frontend.
            bot: The bot.
        """
        super().__init__(frontend, bot)

        # Initialize the decks file if it does not exist
        self._deck_file = "decks.json"
        self._decks = {}
        if not exists(self._deck_file):
            self.save_decks()

        # Load the decks from disk
        with open(self._deck_file, "r") as f:
            self._decks = load(f, object_hook=Deck.unjson)

    def save_decks(self):
        """Saves all decks."""
        with open(self._deck_file, "w") as f:
            dump(self._decks, f, indent=4, sort_keys=True, default=Deck.json)

    async def on_command(self, msg, cmd, args):
        """Event handler for commands.

        Args:
            msg: The message.
            cmd: The command label.
            args: The command arguments.
        """
        if cmd != "kgf":
            return

        syntax = "Syntax: `.kgf <list|create <deck>|stats <deck>>`"

        if len(args) == 0:
            await msg.channel.send(syntax)
            return

        admin_ids = self._frontend.config.get("admins", [])
        admin = msg.author.id in admin_ids

        if args[0] == "list":
            await self._cmd_list(msg.channel)
            return

        if len(args) < 2:
            await msg.channel.send(syntax)
            return
        deck = args[1].lower()

        if args[0] == "create":
            if admin:
                await self._cmd_create(msg.channel, deck)
            else:
                await self._perm_error(msg.channel)

        if deck not in self._decks:
            await self._error(channel, "Unknown Deck",
                              "That deck name is unknown.")
            return
        deck_name = deck
        deck = self._decks[deck]

        if args[0] == "stats":
            await self._cmd_stats(msg.channel, deck)

        if not deck.public and not admin:
            await self._error(channel, "Private Deck", "This deck is private.")

        # TODO

    async def _cmd_list(self, channel):
        """Handles the list subcommand.

        Args:
            channel: The channel in which the command was executed.
        """
        if len(self._decks) == 0:
            await channel.send("Currently 0 decks.")
        else:
            deck_keys = (k for k in self._decks)
            decks = ", ".join(map(lambda s: "`%s`" % s, deck_keys))
            await channel.send("Currently %d deck(s): %s"
                               % (len(self._decks), decks))

    async def _cmd_create(self, channel, deck):
        """Handles the create subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The requested deck name."
        """
        deck = deck.lower()
        if deck in self._decks:
            await self._error(channel, "Name Taken",
                              "This name is already taken.")
            return

        self._decks[deck] = Deck()
        self.save_decks()
        await channel.send("Deck created.")

    async def _cmd_stats(self, channel, deck):
        """Handles the stats subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The requested deck."
        """
        stats = deck.card_stats()

        fmt = "%d cards total (%d statements, %d objects, %d verbs), Public: %r"
        await channel.send(fmt % (stats["TOTAL"], stats["STATEMENT"],
                                  stats["OBJECT"], stats["VERB"], deck.public))

    async def _input(self, author, channel):
        """Attempts to wait for a message by the given author.

        Args:
            author: The author to wait for.
            channel: The channel which is monitored.

        Returns:
            The message that was received, or None.
        """
        try:
            pred = lambda m: m.author == author and m.channel == channel
            response = await self._bot.wait_for("message", check=pred,
                                                timeout=60.0)
            return response
        except asyncio.TimeoutError:
            await channel.send("Request timed out.")
            return None

    async def _perm_error(self, channel):
        """Sends a permission error to the given channel.

        Args:
            channel: The channel.
        """
        await self._error(channel, "Insufficient Permissions", "You need to"
                          + " be whitelisted in order to do this.")

    async def _error(self, channel, title, content):
        """Sends an error to the given channel.

        Args:
            channel: The channel.
            title: The title of the error.
            content: The error message.
        """
        embed = create_embed("Error - " + title, content, 0xAA0000)
        await channel.send(embed=embed)
