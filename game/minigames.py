import pygame
import random
import time
from config import *

# Touches faciles sur PC portable, réparties par joueur pour 2 joueurs sur le même clavier
# Joueur 1: gauche du clavier | Joueur 2: droite du clavier (pas de chevauchement)
MINIGAME_KEYS_PLAYER1 = [
    (pygame.K_1, '1'), (pygame.K_2, '2'), (pygame.K_3, '3'), (pygame.K_4, '4'),
]
MINIGAME_KEYS_PLAYER2 = [
    (pygame.K_7, '7'), (pygame.K_8, '8'), (pygame.K_9, '9'), (pygame.K_0, '0'),
]


class MiniGame:
    def __init__(self, dish_name, player_index=0):
        self.dish_name = dish_name
        self.player_index = player_index
        self.active = True
        self.start_time = time.time()
        self.duration = 5.0
        self.completed = False
        self.success = False
        # Séquence de touches propre à ce joueur, ordre mélangé à chaque partie
        key_set = list(MINIGAME_KEYS_PLAYER1 if player_index == 0 else MINIGAME_KEYS_PLAYER2)
        random.shuffle(key_set)
        self.required_keys = [k for k, _ in key_set]
        self.key_names = [name for _, name in key_set]
        self.current_step = 0
        
    def update(self, events):
        if not self.active: return
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Ne réagir qu'aux touches de notre séquence (évite que la touche du coéquipier nous réinitialise)
                if event.key not in self.required_keys:
                    continue
                if event.key == self.required_keys[self.current_step]:
                    self.current_step += 1
                    if self.current_step >= len(self.required_keys):
                        self.success = True
                        self.completed = True
                        self.active = False
                else:
                    self.current_step = 0
                    
        if time.time() - self.start_time > self.duration:
            self.success = False
            self.completed = True
            self.active = False
            
    def draw(self, surface, x, y):
        # Larger mini-game UI
        width = 280
        height = 120
        
        # Background
        bg_rect = pygame.Rect(x - 20, y - 20, width, height)
        pygame.draw.rect(surface, (40, 40, 50), bg_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 200, 50), bg_rect, 3, border_radius=10)
        
        # Title
        font = pygame.font.SysFont(None, 28)
        title = font.render(f"Préparation: {self.dish_name}", True, WHITE)
        surface.blit(title, (x - 10, y - 10))
        
        # Key sequence display
        key_font = pygame.font.SysFont(None, 36)
        key_x = x
        for i, key_name in enumerate(self.key_names):
            color = GREEN if i < self.current_step else (WHITE if i == self.current_step else GRAY)
            key_bg = pygame.Rect(key_x, y + 30, 50, 50)
            pygame.draw.rect(surface, color, key_bg, border_radius=8)
            pygame.draw.rect(surface, BLACK, key_bg, 2, border_radius=8)
            key_text = key_font.render(key_name, True, BLACK)
            surface.blit(key_text, (key_x + 15, y + 40))
            key_x += 60
            
        # Timer bar
        elapsed = time.time() - self.start_time
        remaining_ratio = max(0, 1 - elapsed / self.duration)
        bar_width = int(240 * remaining_ratio)
        pygame.draw.rect(surface, GRAY, (x - 10, y + 85, 240, 15), border_radius=5)
        bar_color = GREEN if remaining_ratio > 0.3 else ORANGE if remaining_ratio > 0.1 else RED
        pygame.draw.rect(surface, bar_color, (x - 10, y + 85, bar_width, 15), border_radius=5)
