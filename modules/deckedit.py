import asyncio
import discord
import io
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

        # Set search result limit
        self._results_limit = self._frontend.config.get("search-result-limit",
                                                        10)

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
        await msg.channel.trigger_typing()

        syntax = "Syntax: .kgf <list" \
                 + "|create <deck>" \
                 + "|remove-deck <deck>" \
                 + "|stats <deck>" \
                 + "|add <deck> <type> <text...>" \
		 + "|replace <deck> <id> <type> <text...>" \
                 + "|search <deck> <query...>" \
                 + "|delete <deck> <id>" \
                 + "|download <deck>" \
                 + "|export <deck>>"

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
            return

        if deck not in self._decks:
            await self._error(msg.channel, "Unknown Deck",
                              "That deck name is unknown.")
            return
        deck_name = deck
        deck = self._decks[deck]

        if args[0] == "stats":
            await self._cmd_stats(msg.channel, deck)

        if args[0] == "download":
            await self._cmd_download(msg.channel, deck, deck_name)

        if args[0] == "export":
            await self._cmd_export(msg.channel, deck, deck_name)

        if args[0] == "add" and len(args) >= 4:
            await self._cmd_add(msg.channel, deck, args[2], " ".join(args[3:]))

        if args[0] == "replace" and len(args) >= 5:
            try:
                id = int(args[2])
            except:
                pass
            else:
                await self._cmd_replace(msg.channel, deck, id, args[3], " ".join(args[4:]))

        if args[0] == "search" and len(args) >= 3:
            await self._cmd_search(msg.channel, deck, " ".join(args[2:]))

        if args[0] == "delete" and len(args) == 3:
            try:
                id = int(args[2])
            except:
                pass
            else:
                await self._cmd_delete(msg.channel, deck, id)

        if args[0] == "remove-deck":
            if admin:
                await self._cmd_remove_deck(msg.channel, deck_name)
            else:
                await self._perm_error(msg.channel)
            return

    async def _cmd_delete(self, channel, deck, id):
        """Handles the delete subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The deck that was requested.
            id: The card ID to delete.
        """
        if len(deck.cards) <= id or id < 0:
            await self._error(channel, "Invalid ID", "This ID is invalid.")
            return

        del deck.cards[id]
        await channel.send("Card Removed -- WARNING: Card IDs have changed!")

    async def _cmd_download(self, channel, deck, deckname):
        """Handles the download subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The requested deck.
            deckname: The name of the requested deck.
        """
        desc = "KgF Deck (DO NOT USE THIS FILE TO PLAY)\r\n\r\n"
        fmt = "#%d (%s) -- %s\r\n"
        for i, card in enumerate(deck.cards):
            desc += fmt % (i, card[0], card[1])
        fp = discord.File(io.BytesIO(desc.encode()), deckname + ".txt")
        await channel.send("Evaluation Download -- Not usable for playing",
                           file=fp)

    async def _cmd_export(self, channel, deck, deckname):
        """Handles the export subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The requested deck.
            deckname: The name of the requested deck.
        """
        desc = ""
        fmt = "%s\t%s\n"
        for card in deck.cards:
            desc += fmt % (card[1], card[0])
        fp = discord.File(io.BytesIO(desc.encode()), deckname + ".tsv")
        await channel.send("Deck Export -- Ready for playing", file=fp)

    async def _cmd_remove_deck(self, channel, deckname):
        """Handles the remove-deck subcommand.

        Args:
            channel: The channel in which the command was executed.
            deckname: The name of the deck.
        """
        del self._decks[deckname]
        self.save_decks()
        await channel.send("Deck removed.")

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

    async def _cmd_add(self, channel, deck, type, text):
        """Handles the add subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The requested deck.
            type: The requested card type.
            text: The requested text for the card.
        """
        try:
            deck.add_card(type, text)
            self.save_decks()
            embed = create_embed("New " + type, "`%s`" % text, 0x00AA00)
            await channel.send(embed=embed)
        except ValueError as e:
            await self._error(channel, "Could Not Add", str(e))

    async def _cmd_replace(self, channel, deck, id, type, text):
        """Handles the replace subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The deck that was requested.
            id: The card ID to replace.
            type: The requested card type.
            text: The requested text for the card.
        """
        if len(deck.cards) <= id or id < 0:
            await self._error(channel, "Invalid ID", "This ID is invalid.")
            return
        try:
            deck.add_card(type, text)
            deck.cards[id] = deck.cards.pop()
            self.save_decks()
            embed = create_embed("Replaced card #%d with %s" % (id, type), "`%s`" % text, 0x00AA00)
            await channel.send(embed=embed)
        except ValueError as e:
            await self._error(channel, "Could Not Add", str(e))

    async def _cmd_search(self, channel, deck, query):
        """Handles the search subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The requested deck.
            query: The search query.
        """
        results = []
        search_results = 0
        query = query.lower()
        for id, entry in enumerate(deck.cards):
            _, card = entry
            if query in card.lower():
                if search_results < self._results_limit:
                    results.append((id, card))
                search_results += 1
        title = "Search Results"
        if search_results > self._results_limit:
            title += " (showing first %d of %d results)" % (self._results_limit,
                                                            search_results)
        if search_results == 0:
            title = "No Results"
        msg = "\n".join(["#%d: `%s`" % (id, card) for id, card in results])
        embed = create_embed(title, msg, 0x00AA00)
        await channel.send(embed=embed)

    async def _cmd_stats(self, channel, deck):
        """Handles the stats subcommand.

        Args:
            channel: The channel in which the command was executed.
            deck: The requested deck."
        """
        stats = deck.card_stats()

        fmt = "%d card(s) total (%d statement(s), %d object(s), %d verb(s))"
        await channel.send(fmt % (stats["TOTAL"], stats["STATEMENT"],
                                  stats["OBJECT"], stats["VERB"]))

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
