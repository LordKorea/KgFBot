class Deck:

    def __init__(self):
        """Constructor."""
        self.cards = []

    def add_card(self, category, text):
        """Adds a card to the deck.

        Args:
            category: The card category.
            text: The card text.
        """
        category = category.upper()

        # Sanity check for categories
        if category not in {"STATEMENT", "OBJECT", "VERB"}:
            raise ValueError("Invalid category")

        # Sanity check for gaps
        gaps = text.count("_")
        if gaps > 3:
            raise ValueError("Can have at most 3 gaps")
        if gaps > 0 and category != "STATEMENT":
            raise ValueError("Can only have gaps in statements")
        if gaps == 0 and category == "STATEMENT":
            raise ValueError("Need at least one gap in statements")

        card = (category, text)
        if card in self.cards:
            raise ValueError("Card already existing")

        self.cards.append(card)

    def card_stats(self):
        """Returns card stats.

        Returns:
            A dictionary that maps str -> int indicating the number of cards per
            category. Valid categories: STATEMENT, OBJECT, VERB, TOTAL.
        """
        is_x = lambda s: lambda x: x[0] == s
        return {
            "TOTAL": len(self.cards),
            "STATEMENT": len(list(filter(is_x("STATEMENT"), self.cards))),
            "OBJECT": len(list(filter(is_x("OBJECT"), self.cards))),
            "VERB": len(list(filter(is_x("VERB"), self.cards))),
        }

    @staticmethod
    def json(o):
        r = o.__dict__
        r["__class"] = "Deck"
        return r

    @staticmethod
    def unjson(j):
        if "__class" in j and j["__class"] == "Deck":
            del j["__class"]
            o = Deck()
            o.__dict__.update(j)
            return o
        return j
