import pygame
import sys
from config import *
from game.state import GameState
from rendering.split_screen import SplitScreenRenderer
from input.controls import InputHandler
from game.assets_loader import Assets

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SnackAnarchy - Le Roi du Gras")
        
        # Load Assets
        Assets.get().load_images()
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.game_state = GameState()
        self.renderer = SplitScreenRenderer(self.screen)
        self.input_handler = InputHandler()
        
    def restart(self):
        """Restart the game"""
        self.game_state = GameState()
        
    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE and self.game_state.game_over:
                        self.restart()

            # Handle Input
            action = self.input_handler.handle_input(self.game_state.players, events)
            
            # Update Game State
            self.game_state.update(events, action)
            
            # Draw
            self.renderer.draw(self.game_state)
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
