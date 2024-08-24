from card import Card
from deck import Deck
from player import Player
from pot import Pot


game_pot = Pot()
game_deck = Deck()
game_deck.shuffle_deck()


def create_players(num_of_players):
    players = []

    for i in range(num_of_players):
        
        name = input(f'Enter the name of player {i + 1} (or leave blank for CPU player): ')
        
        if name.strip() == '':
            valid_level = False
            while not valid_level:
               level = input('Choose difficulty. (E)asy or (H)ard: ').strip().upper()
               if level == 'E' or level == 'H':
                   break
            player = Player(level=level)
            print()
        else:
            player = Player(name)
        players.append(player)

    return players

def gameloop():
    while True:
        try:
            number_of_players = int(input('Enter the number of players: '))
            if isinstance(number_of_players,int):
                break
        except:
            print('Please enter a valid number\n')
    print()
    players = create_players(number_of_players)

    for player in players:
        print(f'Player added: {player}')
    print()
    game_deck.deal(players)
    print()
    game_won = False

    while not game_won:
        for player in players:
            player.draw_card(game_deck,game_pot)
            if player.get_has_won():
                print(f'***{player.get_player_name()} has won***')
                game_won = True
                break
            if game_won:
                break
            if player.is_cpu:
                print('cpu plays')
                player.cpu_play(game_pot)

            if not player.is_cpu:
                while True:
                    
                    card_to_throw = input('Which card do you want to throw down? ').upper()
                    if card_to_throw in [card.__repr__() for card in player.get_hand()]:
                        player.player_throw_card(card_to_throw,game_pot,players)
                        input()
                        break
                    else:
                        print("You can't lose what you don't have buddy")
                    
gameloop()