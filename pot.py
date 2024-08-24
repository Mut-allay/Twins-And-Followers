import random
class Pot:

    def __init__(self):
        self.__cards_in_pot = []

    
    def add_to_pot(self,card):
        self.__cards_in_pot.append(card)

    def pot_to_deck(self,deck):
        random.shuffle(self.__cards_in_pot)
        deck.cards.extend(self.__cards_in_pot)

        pass