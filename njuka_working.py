import sys
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
                            QHBoxLayout, QMessageBox, QInputDialog)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

suits = ['♠', '♥', '♦', '♣']
values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

def is_winning_combination(cards):
    values_idx = [card.value_index for card in cards]
    value_counts = {}
    for v in values_idx:
        value_counts[v] = value_counts.get(v, 0) + 1
    pairs = [v for v, count in value_counts.items() if count == 2]
    if len(pairs) != 1:
        return False
    pair_value = pairs[0]
    # Remove both pair cards
    remaining = [v for v in values_idx if v != pair_value]
    if len(remaining) != 2:
        remaining = [v for v in values_idx if v != pair_value or (v == pair_value and values_idx.count(v) > 2)]
    remaining = sorted(remaining)
    if len(remaining) != 2:
        return False
    diff = remaining[1] - remaining[0]
    # Ace and 2 wraparound
    return diff == 1 or remaining == [1, 2]

def check_any_player_win(players, pot):
    """Returns the winning player object if someone has a win, else None."""
    pot_top = pot[-1] if pot else None
    for player in players:
        # Win with 4 cards in hand
        if len(player.hand) == 4 and is_winning_combination(player.hand):
            return player
        # Win with 3 cards in hand + top of pot (no swapping, just combine)
        if pot_top and len(player.hand) == 3:
            if is_winning_combination(player.hand + [pot_top]):
                return player
    return None

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.value_index = values.index(value) + 1
        self.id = f"{value}{suit}"

    def __str__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, Card) and self.id == other.id

class Deck:
    def __init__(self):
        self.cards = []
        self.dealt_cards = set()
        for suit in suits:
            for value in values:
                card = Card(value, suit)
                self.cards.append(card)
        assert len(self.cards) == 52, f"Deck must have 52 cards, got {len(self.cards)}"
        assert len({card.id for card in self.cards}) == 52, "Deck contains duplicate cards!"
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            return None
        card = self.cards.pop(0)
        if card.id in self.dealt_cards:
            raise ValueError(f"Duplicate card detected: {card.id}")
        self.dealt_cards.add(card.id)
        return card

    def is_empty(self):
        return len(self.cards) == 0

    def add_cards(self, cards):
        for card in cards:
            if card.id not in self.dealt_cards:
                raise ValueError(f"Can't add undealt card: {card.id}")
            self.dealt_cards.remove(card.id)
        self.cards.extend(cards)
        random.shuffle(self.cards)

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.wins = 0

    def draw(self, deck):
        if len(self.hand) >= 4:
            raise ValueError("Hand already has 4 cards, cannot draw another.")
        card = deck.draw()
        if card:
            assert card not in self.hand, "Cannot add duplicate card to hand."
            self.hand.append(card)
            assert len(self.hand) <= 4, "Hand overflow: more than 4 cards."
        return card

    def discard(self, index):
        if not (0 <= index < len(self.hand)):
            raise IndexError("Discard index out of range.")
        card_to_discard = self.hand[index]
        removed = self.hand.pop(index)
        assert removed == card_to_discard, "Discarded card does not match expected."
        return removed

class Game(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_game()

    def init_ui(self):
        self.setWindowTitle("Pair & Follow")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QWidget { background-color: #2E8B57; }
            QLabel { 
                background-color: white;
                border-radius: 8px;
                padding: 5px;
            }
            QPushButton {
                background-color: #FFD700;
                border: 2px solid #8B4513;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #FFEC8B; }
        """)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.top_controls = QHBoxLayout()
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.clicked.connect(self.new_game)
        self.top_controls.addWidget(self.new_game_btn)
        self.stats_label = QLabel("Wins: You (0) | CPU (0)")
        self.top_controls.addWidget(self.stats_label)
        self.top_controls.addStretch()
        self.main_layout.addLayout(self.top_controls)

        self.game_area = QHBoxLayout()
        self.deck_pot_area = QVBoxLayout()
        self.deck_label = QLabel("Deck\n(52)")
        self.deck_label.setAlignment(Qt.AlignCenter)
        self.deck_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.deck_label.setFixedSize(100, 150)
        self.deck_label.setStyleSheet("""
            background-color: #4169E1;
            color: white;
            border: 3px solid #000080;
            border-radius: 10px;
        """)
        self.deck_pot_area.addWidget(self.deck_label)

        self.pot_label = QLabel("Pot\n(0)")
        self.pot_label.setAlignment(Qt.AlignCenter)
        self.pot_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.pot_label.setFixedSize(100, 150)
        self.pot_label.setStyleSheet("""
            background-color: #DC143C;
            color: white;
            border: 3px solid #8B0000;
            border-radius: 10px;
        """)
        self.deck_pot_area.addWidget(self.pot_label)
        self.game_area.addLayout(self.deck_pot_area)
        self.game_area.addStretch()

        self.player_hand_area = QVBoxLayout()
        self.cpu_hand_label = QLabel("CPU Hand")
        self.cpu_hand_label.setFont(QFont('Arial', 12))
        self.cpu_hand_label.setAlignment(Qt.AlignCenter)
        self.player_hand_area.addWidget(self.cpu_hand_label)
        self.cpu_hand_layout = QHBoxLayout()
        self.cpu_hand_layout.setSpacing(10)
        self.player_hand_area.addLayout(self.cpu_hand_layout)
        self.player_hand_label = QLabel("Your Hand")
        self.player_hand_label.setFont(QFont('Arial', 12))
        self.player_hand_label.setAlignment(Qt.AlignCenter)
        self.player_hand_area.addWidget(self.player_hand_label)
        self.hand_layout = QHBoxLayout()
        self.hand_layout.setSpacing(10)
        self.player_hand_area.addLayout(self.hand_layout)
        self.game_area.addLayout(self.player_hand_area)
        self.main_layout.addLayout(self.game_area)

        self.status_label = QLabel("Welcome to Pair & Follow!")
        self.status_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        self.controls_layout = QHBoxLayout()
        self.draw_button = QPushButton("Draw from Deck")
        self.draw_button.clicked.connect(self.draw_card)
        self.draw_button.setFixedWidth(200)
        self.controls_layout.addWidget(self.draw_button)
        self.main_layout.addLayout(self.controls_layout)

    def init_game(self):
        self.deck = None
        self.pot = []
        self.players = []
        self.current_player_index = 0
        self.game_active = False
        self.has_drawn = False
        self.card_widgets = []
        self.player_hand_snapshot = []
        self.new_game()

    def new_game(self):
        self.game_active = True
        self.has_drawn = False

        try:
            self.deck = Deck()
            self.pot = []
            self.card_widgets = []

            for i in reversed(range(self.cpu_hand_layout.count())):
                w = self.cpu_hand_layout.itemAt(i).widget()
                if w:
                    w.setParent(None)

            cpu_count, ok = QInputDialog.getInt(self, "CPU Players", "Enter number of CPU opponents (1-3):", 1, 1, 3)
            if not ok:
                return

            self.players = [Player("You")] + [Player(f"CPU {i+1}") for i in range(cpu_count)]

            for _ in range(3):
                for player in self.players:
                    try:
                        card = player.draw(self.deck)
                        if not card:
                            raise ValueError(f"Failed to deal card to {player.name}")
                    except Exception as e:
                        QMessageBox.critical(self, "Game Error", f"Failed to deal card: {str(e)}")
                        self.game_active = False
                        return

            self.current_player_index = random.randint(0, len(self.players)-1)
            self.update_display()
            self.player_hand_snapshot = list(self.players[0].hand)

            # Check for win at start (in case it's possible)
            winner = check_any_player_win(self.players, self.pot)
            if winner:
                self.show_winner(winner)
                return

            if self.current_player_index == 0:
                self.status_label.setText("Your turn! Click 'Draw from Deck'")
                self.draw_button.setEnabled(True)
            else:
                self.status_label.setText(f"{self.players[self.current_player_index].name}'s turn...")
                self.draw_button.setEnabled(False)
                QTimer.singleShot(1000, self.cpu_turn)

        except Exception as e:
            QMessageBox.critical(self, "Game Error", f"Failed to start game: {str(e)}")
            self.game_active = False

    def update_display(self):
        self.update_hand()
        self.update_cpu_hand()
        self.update_pot()
        self.update_stats()

    def update_hand(self):
        current_hand = [card.id for card in self.players[0].hand]
        displayed_hand = [self.hand_layout.itemAt(i).widget().text() 
                         for i in range(self.hand_layout.count()) 
                         if self.hand_layout.itemAt(i).widget()]
        if current_hand != displayed_hand:
            for i in reversed(range(self.hand_layout.count())):
                widget = self.hand_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            self.card_widgets = []
            for idx, card in enumerate(self.players[0].hand):
                self._add_card_widget(card, idx)

    def _add_card_widget(self, card, position):
        card_label = QLabel(str(card))
        card_label.setFont(QFont('Arial', 24))
        card_label.setAlignment(Qt.AlignCenter)
        card_label.setFixedSize(80, 120)
        card_label.setStyleSheet(
            "color: red; border: 2px solid black; background: white; font-weight: bold;" if card.suit in ['♥', '♦']
            else "color: black; border: 2px solid black; background: white; font-weight: bold;"
        )
        card_label.mousePressEvent = lambda event, idx=position: self.discard_card(idx)
        self.hand_layout.insertWidget(position, card_label)
        self.card_widgets.append(card_label)

    def discard_card(self, index):
        if not self.game_active or self.current_player_index != 0:
            return
        if not self.has_drawn:
            QMessageBox.warning(self, "Invalid Move", "You must draw a card first!")
            return
        before_hand = list(self.players[0].hand)
        try:
            discarded_card = self.players[0].discard(index)
        except (IndexError, AssertionError) as e:
            QMessageBox.warning(self, "Discard Error", str(e))
            return
        if discarded_card:
            after_hand = list(self.players[0].hand)
            expected_hand = before_hand[:index] + before_hand[index+1:]
            if after_hand != expected_hand:
                QMessageBox.critical(self, "BUG DETECTED",
                    f"Hand mutated incorrectly on discard.\nBefore: {before_hand}\nAfter: {after_hand}\nExpected: {expected_hand}")
                self.game_active = False
                return
            self.pot.append(discarded_card)
            self.update_display()
            self.player_hand_snapshot = list(self.players[0].hand)

            # Check for win for any player after discard (including 3+pot cases)
            winner = check_any_player_win(self.players, self.pot)
            if winner:
                self.show_winner(winner)
                return

            self.has_drawn = False
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if self.current_player_index == 0:
                QMessageBox.critical(self, "BUG DETECTED", "Turn logic error: Player turn immediately after player turn.")
                self.game_active = False
            else:
                self.status_label.setText(f"{self.players[self.current_player_index].name}'s turn...")
                self.draw_button.setEnabled(False)
                QTimer.singleShot(1000, self.cpu_turn)

    def update_cpu_hand(self):
        for i in reversed(range(self.cpu_hand_layout.count())):
            w = self.cpu_hand_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        if len(self.players) > 1:
            cpu = self.players[1]
            for _ in cpu.hand:
                card_back = QLabel("🂠")
                card_back.setFont(QFont('Arial', 24))
                card_back.setAlignment(Qt.AlignCenter)
                card_back.setFixedSize(80, 120)
                card_back.setStyleSheet("color: black; border: 2px solid black; background: white;")
                self.cpu_hand_layout.addWidget(card_back)

    def update_pot(self):
        if self.pot:
            card = self.pot[-1]
            self.pot_label.setText(f"Pot\n{str(card)}")
            if card.suit in ['♥', '♦']:
                self.pot_label.setStyleSheet("""
                    background-color: #DC143C;
                    color: red;
                    border: 3px solid #8B0000;
                    border-radius: 10px;
                """)
            else:
                self.pot_label.setStyleSheet("""
                    background-color: #DC143C;
                    color: black;
                    border: 3px solid #8B0000;
                    border-radius: 10px;
                """)
        else:
            self.pot_label.setText("Pot\n(0)")
            self.pot_label.setStyleSheet("""
                background-color: #DC143C;
                color: white;
                border: 3px solid #8B0000;
                border-radius: 10px;
            """)
        self.deck_label.setText(f"Deck\n({len(self.deck.cards)})")

    def update_stats(self):
        player_wins = self.players[0].wins
        cpu_wins = sum(p.wins for p in self.players[1:])
        self.stats_label.setText(f"Wins: You ({player_wins}) | CPU ({cpu_wins})")

    def draw_card(self):
        if not self.game_active or self.current_player_index != 0:
            return
        if self.has_drawn:
            QMessageBox.warning(self, "Invalid Move", "You can only draw one card per turn!")
            return
        if len(self.players[0].hand) >= 4:
            QMessageBox.warning(self, "Hand Full", "You already have 4 cards! Discard one first.")
            return
        if self.deck.is_empty():
            if len(self.pot) > 1:
                try:
                    self.deck.add_cards(self.pot[:-1])
                    self.pot = [self.pot[-1]]
                    self.update_display()
                except ValueError as e:
                    QMessageBox.critical(self, "Deck Error", f"Failed to reshuffle: {str(e)}")
                    return
            else:
                QMessageBox.information(self, "Game Over", "No cards left!")
                self.game_active = False
                return
        before_hand = list(self.players[0].hand)
        try:
            drawn_card = self.players[0].draw(self.deck)
        except Exception as e:
            QMessageBox.critical(self, "Draw Error", f"Error drawing card: {str(e)}")
            return
        if drawn_card:
            after_hand = list(self.players[0].hand)
            if after_hand != before_hand + [drawn_card]:
                QMessageBox.critical(self, "BUG DETECTED",
                    f"BUG: Draw did not add card to end of hand.\nBefore: {before_hand}\nAfter: {after_hand}\nDrew: {drawn_card}")
                self.game_active = False
                return
            self.has_drawn = True
            self.update_display()
            self.player_hand_snapshot = list(self.players[0].hand)

            # Check for win for any player after draw (including 3+pot cases)
            winner = check_any_player_win(self.players, self.pot)
            if winner:
                self.show_winner(winner)
            else:
                self.status_label.setText("Select a card to discard")

    def cpu_turn(self):
        if hasattr(self, 'player_hand_snapshot'):
            if self.players[0].hand != self.player_hand_snapshot:
                before, after = self.player_hand_snapshot, self.players[0].hand
                QMessageBox.critical(self, "BUG DETECTED",
                    f"Player's hand changed during CPU turn!\nBefore: {before}\nAfter: {after}")
                self.game_active = False
                return
        if self.current_player_index == 0:
            QMessageBox.critical(self, "BUG DETECTED", "CPU turn called with current_player_index == 0. This should never happen!")
            self.game_active = False
            return
        if not self.game_active:
            return
        cpu = self.players[self.current_player_index]
        try:
            if len(cpu.hand) < 4:
                cpu.draw(self.deck)
                self.update_display()
        except Exception as e:
            QMessageBox.critical(self, "CPU Error", f"CPU draw error: {str(e)}")
            self.game_active = False
            return

        # Check for win for any player after CPU draws (including 3+pot cases)
        winner = check_any_player_win(self.players, self.pot)
        if winner:
            self.show_winner(winner)
            return

        if len(cpu.hand) == 4:
            try:
                discard_index = random.randint(0, 3)
                discarded = cpu.discard(discard_index)
                self.pot.append(discarded)
                self.update_display()
                # Check for win after discard
                winner = check_any_player_win(self.players, self.pot)
                if winner:
                    self.show_winner(winner)
                    return
            except Exception as e:
                QMessageBox.critical(self, "CPU Error", f"CPU discard error: {str(e)}")
                self.game_active = False
                return
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            self.status_label.setText("Your turn! Click 'Draw from Deck'")
            self.draw_button.setEnabled(True)
        else:
            self.status_label.setText(f"{self.players[self.current_player_index].name}'s turn...")
            QTimer.singleShot(1000, self.cpu_turn)

    def show_winner(self, player):
        player.wins += 1
        message = f"{player.name} wins!\n\nFinal hands:\n"
        for p in self.players:
            message += f"{p.name}: {[str(c) for c in p.hand]}\n"
        QMessageBox.information(self, "Game Over", message)
        self.update_stats()
        self.new_game()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Game()
    game.show()
    sys.exit(app.exec_())