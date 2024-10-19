from collections import Counter, namedtuple

Card = namedtuple("Card", ["rank", "color"])


class PokerHand(object):
    RESULT = ["Loss", "Tie", "Win"]
    RANKS = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14} | {
        str(r): r for r in range(1, 10)
    }
    VALUE_MAP = {
        "High Card": 1,
        "Pair": 2,
        "Two Pairs": 3,
        "Three of a Kind": 4,
        "Straight": 5,
        "Flush": 6,
        "Full House": 7,
        "Four of a Kind": 8,
        "Straight Flush": 9,
        "Royal Flush": 10,
    }

    def __init__(self, raw_hand):
        self.hand = list()

        for raw_card in raw_hand.split():
            color = raw_card[1]
            rank = self.RANKS.get(raw_card[0])
            self.hand.append(Card(rank, color))

        self.hand.sort(key=lambda x: x.rank)
        self.cc = Counter(card.rank for card in self.hand)

    def __repr__(self):
        return "-".join(str(c.rank) + c.color for c in self.hand)

    def evaluate(self):
        hand = self.hand
        colors = {card.color for card in hand}
        has_flush = len(colors) == 1

        aces = {card.rank for card in hand if card.rank == 14}
        has_ace = len(aces) > 0

        are_consecutive = [
            (right.rank - left.rank) == 1 for left, right in zip(hand[:-1], hand[1:])
        ]
        has_straight = all(are_consecutive)

        count_cards_by_rank = {}
        for card in self.hand:
            count_cards_by_rank[card.rank] = count_cards_by_rank.get(card.rank, 0) + 1
        max_cards_same_rank = max(count_cards_by_rank.values())
        unique_cards = len(count_cards_by_rank)

        # final evaluation
        if max_cards_same_rank == 1:
            result = "High Card", hand[-1].rank
        elif max_cards_same_rank == 2 and unique_cards == 4:
            result = "Pair", self.cc.most_common()[0]
        elif max_cards_same_rank == 2 and unique_cards == 3:
            result = "Two Pairs", self.cc.most_common()[0]
        elif max_cards_same_rank == 3 and unique_cards == 3:
            result = "Three of a Kind", self.cc.most_common()[0]
        elif max_cards_same_rank == 3 and unique_cards == 2:
            result = "Full House", self.cc.most_common()[0]
        elif max_cards_same_rank == 4:
            result = "Four of a Kind", self.cc.most_common()[0]

        if has_flush and has_straight and has_ace:
            result = "Royal Flush", hand[-1].rank
        elif has_flush and has_straight:
            result = "Straight Flush", hand[-1].rank
        elif has_straight:
            result = "Straight", hand[-1].rank
        elif has_flush:
            result = "Flush", hand[-1].rank

        return result

    def compare_with(self, other):
        self_value, left_high = self.evaluate()
        other_value, right_high = other.evaluate()
        left = self.VALUE_MAP[self_value]
        right = self.VALUE_MAP[other_value]

        if left < right:
            return "Loss"
        elif left > right:
            return "Win"

        if left_high < right_high:
            return "Loss"
        elif left_high > right_high:
            return "Win"

        # pick second most common
        left_most_common = sorted(
            self.cc.most_common(), reverse=True, key=lambda x: (x[1], x[0])
        )
        right_most_common = sorted(
            other.cc.most_common(), reverse=True, key=lambda x: (x[1], x[0])
        )
        for left_i, right_i in zip(left_most_common, right_most_common):
            if left_i < right_i:
                return "Loss"
            elif left_i > right_i:
                return "Win"

        return "Tie"
