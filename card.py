class Card:
    def __init__(self,rank,suit=None,):
        self.__suit = suit
        self.__rank = rank
    def __lt__(self, other):
        # Define rank order for comparison
        rank_order = {'A': 1,'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, }
        # Compare cards by rank
        return rank_order[self.__rank] < rank_order[other.__rank]
    
    def __repr__(self):
        return f"{self.__rank}"
    
    def get_suit(self):
        return self.__suit
    def get_rank(self):
        return self.__rank