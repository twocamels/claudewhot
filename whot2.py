import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Whot Card Game')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BG_COLOR = (50, 150, 100)  # Green table

# Font
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 32)

# Card dimensions
CARD_WIDTH = 80
CARD_HEIGHT = 120

# Define card shapes and their colors
SHAPES = {
    'circle': RED,
    'triangle': BLUE,
    'cross': GREEN,
    'square': YELLOW,
    'star': PURPLE,
    'whot': BLACK
}

# Game state


class WhotGame:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.computer_hand = []
        self.play_pile = []
        self.market_pile = []
        self.game_status = 'initializing'
        self.message = 'Welcome to Whot!'
        self.selected_card = None
        self.whot_shape_request = None
        self.initialize_game()

    def create_deck(self):
        deck = []
        # Add numbered cards for each shape (except whot)
        for shape in list(SHAPES.keys())[:-1]:  # All except 'whot'
            # Add 1-14 cards for each shape
            for num in range(1, 15):
                # Skip 6 and 9 to match official Whot deck
                if num != 6 and num != 9:
                    deck.append({'shape': shape, 'number': num})

        # Add special Whot cards
        for _ in range(5):
            deck.append({'shape': 'whot', 'number': 20})

        return deck

    def initialize_game(self):
        # Shuffle deck
        random.shuffle(self.deck)

        # Deal 7 cards to player and computer
        self.player_hand = self.deck[:7]
        self.computer_hand = self.deck[7:14]

        # Set market pile
        self.market_pile = self.deck[14:-1]

        # Set initial card
        self.play_pile = [self.deck[-1]]

        self.game_status = 'playing'
        self.message = 'Your turn! Play a card or pick from market.'

    def pick_from_market(self):
        if not self.market_pile:
            self.message = 'Market is empty!'
            return False

        card = self.market_pile[0]
        self.market_pile = self.market_pile[1:]

        self.player_hand.append(card)
        self.message = 'You picked from market. Computer\'s turn.'
        return True  # Player picked a card

    def can_play_card(self, card):
        top_card = self.play_pile[-1]

        # Whot card can always be played
        if card['shape'] == 'whot':
            return True

        # If top card is a Whot and a shape was requested
        if top_card['shape'] == 'whot' and self.whot_shape_request:
            return card['shape'] == self.whot_shape_request

        # Regular matching (shape or number)
        return card['shape'] == top_card['shape'] or card['number'] == top_card['number']

    def play_card(self, card_index):
        if not (0 <= card_index < len(self.player_hand)):
            return False

        card = self.player_hand[card_index]

        if not self.can_play_card(card):
            self.message = 'Invalid move! Card must match shape or number'
            return False

        # Remove card from player's hand
        self.player_hand.pop(card_index)

        # Add card to play pile
        self.play_pile.append(card)
        self.selected_card = None

        # Check win condition
        if len(self.player_hand) == 0:
            self.message = 'You win! 🎉'
            self.game_status = 'ended'
            return True

        # Handle special cards
        if card['shape'] == 'whot':
            self.game_status = 'whotRequest'
            self.message = 'You played a Whot card! Select a shape to request:'
            return True

        if card['number'] == 2:
            # Pick two
            self.pick_cards_from_market(2, 'computer')
            self.message = 'Computer picks 2! Your turn again.'
            return True

        if card['number'] == 14:
            # General Market
            self.pick_cards_from_market(1, 'computer')
            self.message = 'General Market! Computer picks 1. Your turn again.'
            return True

        # Computer's turn
        self.message = 'Computer\'s turn...'
        return True

    def request_shape(self, shape):
        self.whot_shape_request = shape
        self.message = f'You requested {shape}. Computer\'s turn...'
        self.game_status = 'playing'
        return True

    def pick_cards_from_market(self, count, player):
        if len(self.market_pile) < count:
            count = len(self.market_pile)

        cards = self.market_pile[:count]
        self.market_pile = self.market_pile[count:]

        if player == 'player':
            self.player_hand.extend(cards)
        else:
            self.computer_hand.extend(cards)

    def computer_play(self):
        # Find playable cards
        top_card = self.play_pile[-1]
        playable_cards = []

        for i, card in enumerate(self.computer_hand):
            # Whot card can always be played
            if card['shape'] == 'whot':
                playable_cards.append(i)
                continue

            # Check if card matches requested shape from whot
            if top_card['shape'] == 'whot' and self.whot_shape_request:
                if card['shape'] == self.whot_shape_request:
                    playable_cards.append(i)
                continue

            # Regular matching (shape or number)
            if card['shape'] == top_card['shape'] or card['number'] == top_card['number']:
                playable_cards.append(i)

        # If no playable cards, pick from market
        if not playable_cards:
            if self.market_pile:
                card = self.market_pile[0]
                self.market_pile = self.market_pile[1:]
                self.computer_hand.append(card)
                self.message = 'Computer picked from market. Your turn!'
            else:
                self.message = 'Market is empty! Your turn!'
            return

        # Play a random card from playable cards
        card_index = random.choice(playable_cards)
        card = self.computer_hand.pop(card_index)
        self.play_pile.append(card)

        # Check win condition
        if len(self.computer_hand) == 0:
            self.message = 'Computer wins! 😢'
            self.game_status = 'ended'
            return

        # Handle special cards
        if card['shape'] == 'whot':
            # Computer chooses most common shape in its hand
            shapes = {}
            for c in self.computer_hand:
                if c['shape'] != 'whot':
                    shapes[c['shape']] = shapes.get(c['shape'], 0) + 1

            if shapes:
                most_common = max(shapes, key=shapes.get)
                self.whot_shape_request = most_common
                self.message = f'Computer played a Whot and requests {most_common}. Your turn!'
            else:
                # If only whot cards left, choose a random shape
                self.whot_shape_request = random.choice(
                    list(SHAPES.keys())[:-1])
                self.message = f'Computer played a Whot and requests {self.whot_shape_request}. Your turn!'
            return

        if card['number'] == 2:
            # Pick two
            self.pick_cards_from_market(2, 'player')
            self.message = 'You pick 2! Computer\'s turn again.'
            # Computer plays again
            self.computer_play()
            return

        if card['number'] == 14:
            # General Market
            self.pick_cards_from_market(1, 'player')
            self.message = 'General Market! You pick 1. Computer\'s turn again.'
            # Computer plays again
            self.computer_play()
            return

        self.message = 'Computer played a card. Your turn!'

# Main game loop


def main():
    clock = pygame.time.Clock()
    game = WhotGame()
    computer_turn_timer = 0
    waiting_for_computer = False

    # Helper function to draw a card
    def draw_card(card, x, y, selected=False):
        # Draw card background
        border_color = WHITE
        if selected:
            border_color = (255, 215, 0)  # Gold for selected card

        pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, border_color,
                         (x, y, CARD_WIDTH, CARD_HEIGHT), 3)

        # Draw card shape and number
        shape = card['shape']
        number = card['number']
        color = SHAPES[shape]

        # Draw number at top-left and bottom-right
        number_text = font.render(str(number), True, color)
        screen.blit(number_text, (x + 5, y + 5))
        screen.blit(number_text, (x + CARD_WIDTH - 25, y + CARD_HEIGHT - 30))

        # Draw shape symbol in center
        if shape == 'circle':
            pygame.draw.circle(
                screen, color, (x + CARD_WIDTH//2, y + CARD_HEIGHT//2), 20)
        elif shape == 'triangle':
            points = [(x + CARD_WIDTH//2, y + CARD_HEIGHT//2 - 20),
                      (x + CARD_WIDTH//2 - 20, y + CARD_HEIGHT//2 + 10),
                      (x + CARD_WIDTH//2 + 20, y + CARD_HEIGHT//2 + 10)]
            pygame.draw.polygon(screen, color, points)
        elif shape == 'cross':
            pygame.draw.line(screen, color, (x + CARD_WIDTH//2 - 15, y + CARD_HEIGHT//2),
                             (x + CARD_WIDTH//2 + 15, y + CARD_HEIGHT//2), 5)
            pygame.draw.line(screen, color, (x + CARD_WIDTH//2, y + CARD_HEIGHT//2 - 15),
                             (x + CARD_WIDTH//2, y + CARD_HEIGHT//2 + 15), 5)
        elif shape == 'square':
            pygame.draw.rect(screen, color, (x + CARD_WIDTH //
                             2 - 15, y + CARD_HEIGHT//2 - 15, 30, 30))
        elif shape == 'star':
            # Simple star representation
            pygame.draw.polygon(screen, color, [
                (x + CARD_WIDTH//2, y + CARD_HEIGHT//2 - 20),  # Top point
                (x + CARD_WIDTH//2 + 5, y + CARD_HEIGHT//2 - 5),
                (x + CARD_WIDTH//2 + 20, y + CARD_HEIGHT//2 - 5),  # Right top
                (x + CARD_WIDTH//2 + 8, y + CARD_HEIGHT//2 + 5),
                (x + CARD_WIDTH//2 + 15, y + CARD_HEIGHT//2 + 20),  # Right bottom
                (x + CARD_WIDTH//2, y + CARD_HEIGHT//2 + 10),
                (x + CARD_WIDTH//2 - 15, y + CARD_HEIGHT//2 + 20),  # Left bottom
                (x + CARD_WIDTH//2 - 8, y + CARD_HEIGHT//2 + 5),
                (x + CARD_WIDTH//2 - 20, y + CARD_HEIGHT//2 - 5),  # Left top
                (x + CARD_WIDTH//2 - 5, y + CARD_HEIGHT//2 - 5)
            ])
        elif shape == 'whot':
            whot_text = large_font.render('W', True, color)
            screen.blit(whot_text, (x + CARD_WIDTH //
                        2 - 10, y + CARD_HEIGHT//2 - 15))

    # Game loop
    running = True
    while running:
        # Fill the background
        screen.fill(BG_COLOR)

        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos

                if game.game_status == 'playing' and not waiting_for_computer:
                    # Check if player clicked on a card in their hand
                    card_spacing = min(
                        CARD_WIDTH, (SCREEN_WIDTH - 100) // max(1, len(game.player_hand)))
                    for i in range(len(game.player_hand)):
                        card_x = 50 + i * card_spacing
                        card_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
                        card_rect = pygame.Rect(
                            card_x, card_y, CARD_WIDTH, CARD_HEIGHT)

                        if card_rect.collidepoint(mouse_x, mouse_y):
                            if game.play_card(i):
                                # Card was played successfully
                                if game.message.startswith('Computer\'s turn'):
                                    computer_turn_timer = pygame.time.get_ticks()
                                    waiting_for_computer = True
                            break

                    # Check if player clicked on market pile
                    market_x = SCREEN_WIDTH - CARD_WIDTH - 50
                    market_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
                    market_rect = pygame.Rect(
                        market_x, market_y, CARD_WIDTH, CARD_HEIGHT)

                    if market_rect.collidepoint(mouse_x, mouse_y):
                        if game.pick_from_market():
                            computer_turn_timer = pygame.time.get_ticks()
                            waiting_for_computer = True

                elif game.game_status == 'whotRequest':
                    # Check if player clicked on a shape button
                    button_width = 100
                    button_height = 40
                    button_spacing = 20
                    button_y = 400

                    # All except whot
                    for i, shape in enumerate(list(SHAPES.keys())[:-1]):
                        button_x = 150 + i * (button_width + button_spacing)
                        button_rect = pygame.Rect(
                            button_x, button_y, button_width, button_height)

                        if button_rect.collidepoint(mouse_x, mouse_y):
                            if game.request_shape(shape):
                                computer_turn_timer = pygame.time.get_ticks()
                                waiting_for_computer = True
                            break

                elif game.game_status == 'ended':
                    # Check if player clicked on restart button
                    button_x = SCREEN_WIDTH // 2 - 75
                    button_y = SCREEN_HEIGHT // 2 + 50
                    button_rect = pygame.Rect(button_x, button_y, 150, 50)

                    if button_rect.collidepoint(mouse_x, mouse_y):
                        game = WhotGame()  # Reset the game
                        waiting_for_computer = False

        # Computer's turn logic
        if waiting_for_computer and game.game_status == 'playing':
            current_time = pygame.time.get_ticks()
            if current_time - computer_turn_timer > 1000:  # Wait 1 second before computer plays
                game.computer_play()
                waiting_for_computer = False

        # Draw game elements

        # Draw message - FIX: Clear background behind text
        message_text = large_font.render(game.message, True, WHITE)
        message_bg_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - message_text.get_width() // 2 - 10,
            20 - 5,
            message_text.get_width() + 20,
            message_text.get_height() + 10
        )
        pygame.draw.rect(screen, BG_COLOR, message_bg_rect)  # Clear background
        screen.blit(message_text, (SCREEN_WIDTH // 2 -
                    message_text.get_width() // 2, 20))

        # Draw play pile
        if game.play_pile:
            top_card = game.play_pile[-1]
            draw_card(top_card, SCREEN_WIDTH // 2 - CARD_WIDTH //
                      2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)

        # Draw market pile (face down)
        if game.market_pile:
            market_x = SCREEN_WIDTH - CARD_WIDTH - 50
            market_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
            pygame.draw.rect(
                screen, BLUE, (market_x, market_y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(
                screen, WHITE, (market_x, market_y, CARD_WIDTH, CARD_HEIGHT), 3)
            market_text = font.render(
                f'Market ({len(game.market_pile)})', True, WHITE)

            # FIX: Clear background behind text
            market_bg_rect = pygame.Rect(
                market_x - 10 - 5,
                market_y - 30 - 5,
                market_text.get_width() + 10,
                market_text.get_height() + 10
            )
            # Clear background
            pygame.draw.rect(screen, BG_COLOR, market_bg_rect)
            screen.blit(market_text, (market_x - 10, market_y - 30))

        # Draw player's hand
        card_spacing = min(CARD_WIDTH, (SCREEN_WIDTH - 100) //
                           max(1, len(game.player_hand)))
        for i, card in enumerate(game.player_hand):
            card_x = 50 + i * card_spacing
            card_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
            draw_card(card, card_x, card_y, selected=(i == game.selected_card))

        # Draw computer's hand (face down)
        card_spacing = min(CARD_WIDTH, (SCREEN_WIDTH - 100) //
                           max(1, len(game.computer_hand)))
        for i in range(len(game.computer_hand)):
            card_x = 50 + i * card_spacing
            card_y = 50
            pygame.draw.rect(
                screen, RED, (card_x, card_y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(screen, WHITE, (card_x, card_y,
                             CARD_WIDTH, CARD_HEIGHT), 3)

        # Draw computer hand count
        computer_text = font.render(
            f'Computer: {len(game.computer_hand)} cards', True, WHITE)
        # FIX: Clear background behind text
        computer_bg_rect = pygame.Rect(
            50 - 5,
            20 - 5,
            computer_text.get_width() + 10,
            computer_text.get_height() + 10
        )
        # Clear background
        pygame.draw.rect(screen, BG_COLOR, computer_bg_rect)
        screen.blit(computer_text, (50, 20))

        # Draw Whot shape request buttons if needed
        if game.game_status == 'whotRequest':
            # FIX: Add a background for the buttons to make them more visible
            instruction_text = font.render(
                "Select a shape to request:", True, WHITE)
            instruction_bg_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - instruction_text.get_width() // 2 - 5,
                360 - 5,
                instruction_text.get_width() + 10,
                instruction_text.get_height() + 10
            )
            pygame.draw.rect(screen, BG_COLOR, instruction_bg_rect)
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 -
                        instruction_text.get_width() // 2, 360))

            button_width = 100
            button_height = 40
            button_spacing = 20
            button_y = 400

            # All except whot
            for i, shape in enumerate(list(SHAPES.keys())[:-1]):
                button_x = 150 + i * (button_width + button_spacing)

                # Draw button
                pygame.draw.rect(
                    screen, SHAPES[shape], (button_x, button_y, button_width, button_height))
                pygame.draw.rect(
                    screen, WHITE, (button_x, button_y, button_width, button_height), 2)

                # Draw button text
                button_text = font.render(shape, True, WHITE)
                screen.blit(button_text, (button_x + button_width//2 - button_text.get_width()//2,
                                          button_y + button_height//2 - button_text.get_height()//2))

        # Draw restart button if game ended
        if game.game_status == 'ended':
            button_x = SCREEN_WIDTH // 2 - 75
            button_y = SCREEN_HEIGHT // 2 + 50

            pygame.draw.rect(screen, GREEN, (button_x, button_y, 150, 50))
            pygame.draw.rect(screen, WHITE, (button_x, button_y, 150, 50), 2)

            button_text = font.render('Play Again', True, WHITE)
            screen.blit(button_text, (button_x + 75 - button_text.get_width()//2,
                                      button_y + 25 - button_text.get_height()//2))

        # Draw Whot shape request indicator if active
        if game.whot_shape_request:
            request_text = font.render(
                f'Requested shape: {game.whot_shape_request}', True, WHITE)
            # FIX: Clear background behind text
            request_bg_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - request_text.get_width() // 2 - 5,
                60 - 5,
                request_text.get_width() + 10,
                request_text.get_height() + 10
            )
            # Clear background
            pygame.draw.rect(screen, BG_COLOR, request_bg_rect)
            screen.blit(request_text, (SCREEN_WIDTH // 2 -
                        request_text.get_width() // 2, 60))

        # Update the display
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
