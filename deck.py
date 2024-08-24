import random
from card import Card
"""
4 suits
hearts = '\u2665' 
diamonds = '\u2666'
clubs = '\u2663'
spades = '\u2660'

52 cards

"""


class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()

    def shuffle_deck(self):
            random.shuffle(self.cards)

    def create_deck(self):
        suits = ['\u2665','\u2666','\u2663','\u2660']
        ranks = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
        cards = [Card(rank,suit) for rank in ranks for suit in suits]
        self.cards.extend(cards)


    def deal(self,players):
        
        for player in players:
            
            if not player.get_hand():
                deal = self.cards[-3:]
                self.cards = self.cards[:-3]
                player.get_hand().extend(deal)
                player.get_hand().sort()
                if not player.is_cpu:
                     player.print_cards()
                     input('Press Enter')
              