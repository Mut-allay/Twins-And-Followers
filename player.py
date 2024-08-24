import random

class Player:
    def __init__(self,player_name='cpu_player',level=None):
        self.__player_name = player_name
        self.level = level
        self.is_cpu = True if player_name == 'cpu_player' else False
        self.__hand = []
        self.__has_won = False
        self.__ranks = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
 

 
    def print_cards(self):
      
                
                # ASCII representation of each card
                    card_lines = []
                    for card in self.__hand:
                        card_str = f"""
    +-------+
    | {card.get_rank():<2}    |
    |  {card.get_suit()}    |
    |    {card.get_rank():>2} |
    +-------+
    """
                        card_lines.append(card_str.split('\n'))

                # Initialize rows for each card
                    num_rows = len(card_lines[0])
                    rows = ['' for _ in range(num_rows)]
                    print('Hand:\n')

                            # Combine lines of each card horizontally
                    for i in range(num_rows):
                        for card in card_lines:
                            rows[i] += card[i] + '  '  # Add space between cards

                            # Print each row
                    for row in rows:
                        print(row)

    def draw(self,deck):
            
        new_card = deck.cards.pop(0)
        self.__hand.append(new_card)
        self.__hand.sort()
        if not self.is_cpu:
            print(f'You drew a {new_card.get_rank()}')
            self.print_cards()

        if (self.__hand[0].get_rank() == self.__hand[1].get_rank() or self.__hand[2].get_rank() == self.__hand[3].get_rank()) and ((self.__ranks.index(self.__hand[0].get_rank()) == self.__ranks.index(self.__hand[1].get_rank()) - 1) or (self.__ranks.index(self.__hand[2].get_rank()) == self.__ranks.index(self.__hand[3].get_rank()) - 1)):

            self.__has_won = True
            self.print_cards()

    def draw_card(self,deck,pot):
        if len(self.__hand) == 3:
            if len(deck.cards) == 0:
                pot.pot_to_deck(deck)
                self.draw(deck)
            else:
                 self.draw(deck)
        else:
            print('nope')
            input()

    def check_pot(self,players,card):
        for player in players:
            if player.get_player_name() == self.__player_name:
                continue
            else:
                player.give_hand(card)
                player.sort_hand()
                if (player.get_hand()[0].get_rank() == player.get_hand()[1].get_rank() or player.get_hand()[2].get_rank() == player.get_hand()[3].get_rank()) and ((self.__ranks.index(player.get_hand()[0].get_rank()) == self.__ranks.index(player.get_hand()[1].get_rank()) - 1) or (self.__ranks.index(player.get_hand()[2].get_rank()) == self.__ranks.index(player.get_hand()[3].get_rank()) - 1)):
                    self.set_has_won()
                    print(f'***{player.get_player_name()} has won with {card.get_rank()}***')
                    print()
                    player.print_cards()
                    print('***GAME OVER***')
                    exit()
                else:
                    player.delete_card(card)
     
    def player_throw_card(self,rank,pot,players):
        ranks = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
        if len(self.__hand) == 4 and rank.upper() in ranks:
            for i, card in enumerate(self.__hand):

                if card.get_rank() == rank.upper():
                    self.print_discarded(card)
                    pot.add_to_pot(card)
                    self.check_pot(players,card)
                    del self.__hand[i]
                    break
        self.print_cards()

        
    def cpu_play(self,pot):
        if self.level.upper() == 'E':
              self.cpu_throw_card(pot)
        elif self.level.upper() == 'H':
             self.cpu_throw_card_pro(pot)
        else:
             print('Invalid level')
    
    def print_discarded(self,card):
         
         card_str = f"""
    +-------+
    | {card.get_rank():<2}    |
    |  {card.get_suit()}    |
    |    {card.get_rank():>2} |
    +-------+
    """
         print(card_str)

    def cpu_throw_card(self,pot):

        random_card = random.choice(self.__hand)
        pot.add_to_pot(random_card)
        print(f'{self.__player_name} throws card {random_card}')
        self.__hand.remove(random_card)
        print(f"{self.__player_name} is holding: {[card.__repr__() for card in self.__hand]}")
        self.print_discarded(random_card)
        input()

    def delete_last_2_cards(self,pot):
            random_card = random.choice(self.__hand[2:])
            pot.add_to_pot(random_card)
            print(f'{self.__player_name} throws card {random_card}')
            self.print_discarded(random_card)
            self.__hand.remove(random_card)
            print(f"{self.__player_name} is holding: {[card.__repr__() for card in self.__hand]}")
            input()

    #deletes one of the first 2 cards
    def delete_first_2_cards(self,pot):
            random_card = random.choice(self.__hand[:1])
            pot.add_to_pot(random_card)
            print(f'{self.__player_name} throws card {random_card}')
            self.print_discarded(random_card)
            self.__hand.remove(random_card)
            print(f"{self.__player_name} is holding: {[card.__repr__() for card in self.__hand]}")
            input()

    #deletes first or last card at random
    def delete_2_center_cards(self,pot):
            random_card = random.choice([self.__hand[0],self.__hand[0]])
            pot.add_to_pot(random_card)
            print(f'{self.__player_name} throws card {random_card}')
            self.print_discarded
            self.__hand.remove(random_card)
            print(f"{self.__player_name} is holding: {[card.__repr__() for card in self.__hand]}")
            input()

    def cpu_throw_card_pro(self,pot):
    
        ranks = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
        if self.__hand[0].get_rank() == self.__hand[1].get_rank(): 
            self.delete_last_2_cards(pot)

        elif self.__hand[2].get_rank() == self.__hand[3].get_rank():
            self.delete_first_2_cards(pot)

        elif self.__hand[1].get_rank() == self.__hand[2].get_rank():
            self.delete_2_center_cards(pot)

        elif (ranks.index(self.__hand[0].get_rank()) == ranks.index(self.__hand[1].get_rank()) - 1) and not (self.__hand[2].get_rank() == self.__hand[3].get_rank()):
            self.delete_last_2_cards(pot)

        elif (ranks.index(self.__hand[2].get_rank()) == ranks.index(self.__hand[3].get_rank()) - 1) and not (self.__hand[0].get_rank() == self.__hand[1].get_rank()):
             self.delete_first_2_cards(pot)
        elif (ranks.index(self.__hand[1].get_rank()) == ranks.index(self.__hand[2].get_rank()) - 1) and not (self.__hand[0].get_rank() == self.__hand[1].get_rank()) and not (self.__hand[2].get_rank() == self.__hand[3].get_rank()):
             self.delete_2_center_cards(pot)
        else:
             self.cpu_throw_card(pot)
          

    def __repr__(self):
        return f"{self.__player_name} is holding: {[card.__repr__() for card in self.__hand]}"
    
    def __str__(self):
        return self.__player_name
    
    def get_hand(self):
        return self.__hand
    def give_hand(self,card):
        self.__hand.append(card)
    
    def get_has_won(self):
        return self.__has_won
    
    def set_has_won(self):
         self.__has_won = True
    def get_player_name(self):
         return self.__player_name
    def sort_hand(self):
         self.__hand.sort()

    def delete_card(self,card):
         self.__hand.remove(card)