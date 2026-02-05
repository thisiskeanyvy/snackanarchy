"""
Menu de configuration des touches
"""
import pygame
from config import *
from input.controls import get_key_bindings
from game.audio import play_sound


class KeybindMenu:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.font = pygame.font.SysFont("Arial", 26)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.key_font = pygame.font.SysFont("Arial", 22, bold=True)
        
        # Key bindings
        self.key_bindings = get_key_bindings()
        
        # État
        self.selected_player = 0  # 0 ou 1
        self.selected_action = 0
        self.waiting_for_key = False
        self.actions = ['up', 'down', 'left', 'right', 'interact', 'attack', 'sabotage', 'sweep', 'inventory']
        
        # Dimensions
        self.menu_width = 750
        self.menu_height = 550
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        
    def toggle(self):
        self.visible = not self.visible
        self.waiting_for_key = False
        if self.visible:
            play_sound('menu_select', 'ui')
            
    def close(self):
        self.visible = False
        self.waiting_for_key = False
        
    def handle_input(self, event):
        if not self.visible:
            return None
            
        if event.type == pygame.KEYDOWN:
            # Si on attend une touche
            if self.waiting_for_key:
                if event.key == pygame.K_ESCAPE:
                    self.waiting_for_key = False
                    play_sound('menu_move', 'ui')
                    return "cancel"
                    
                # Vérifier si la touche est déjà utilisée
                player = f'player{self.selected_player + 1}'
                action = self.actions[self.selected_action]
                used, used_player, used_action = self.key_bindings.is_key_used(
                    event.key, exclude_player=player, exclude_action=action
                )
                
                if used:
                    # Touche déjà utilisée
                    play_sound('stock_empty', 'ui')
                    return "key_used"
                    
                # Assigner la nouvelle touche
                self.key_bindings.set_key(player, action, event.key)
                self.waiting_for_key = False
                play_sound('menu_select', 'ui')
                return "key_set"
                
            # Navigation normale
            if event.key == pygame.K_ESCAPE:
                self.close()
                return "close"
                
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.selected_player = 0
                play_sound('menu_move', 'ui')
                return "navigate"
                
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.selected_player = 1
                play_sound('menu_move', 'ui')
                return "navigate"
                
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_action = (self.selected_action - 1) % len(self.actions)
                play_sound('menu_move', 'ui')
                return "navigate"
                
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_action = (self.selected_action + 1) % len(self.actions)
                play_sound('menu_move', 'ui')
                return "navigate"
                
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.waiting_for_key = True
                play_sound('menu_select', 'ui')
                return "wait_key"
                
            # Reset avec R
            if event.key == pygame.K_r:
                player = f'player{self.selected_player + 1}'
                self.key_bindings.reset_to_default(player)
                play_sound('menu_select', 'ui')
                return "reset"
                
        return None
        
    def _draw_arrow_icon(self, surface, direction, x, y, size, color):
        """Dessine une icône de flèche directionnelle"""
        cx, cy = x + size // 2, y + size // 2
        half = size // 2 - 2
        
        if direction == 'up':
            points = [(cx, y + 2), (x + size - 2, y + size - 4), (x + 2, y + size - 4)]
        elif direction == 'down':
            points = [(cx, y + size - 2), (x + 2, y + 4), (x + size - 2, y + 4)]
        elif direction == 'left':
            points = [(x + 2, cy), (x + size - 4, y + 2), (x + size - 4, y + size - 2)]
        elif direction == 'right':
            points = [(x + size - 2, cy), (x + 4, y + 2), (x + 4, y + size - 2)]
        else:
            return
            
        pygame.draw.polygon(surface, color, points)
        
    def _draw_action_icon(self, surface, action, x, y, size, color):
        """Dessine une icône pour chaque type d'action"""
        cx, cy = x + size // 2, y + size // 2
        
        if action in ['up', 'down', 'left', 'right']:
            self._draw_arrow_icon(surface, action, x, y, size, color)
        elif action == 'interact':
            # Main qui sert
            pygame.draw.circle(surface, color, (cx, cy - 2), size // 3, 2)
            pygame.draw.line(surface, color, (cx, cy + 2), (cx, y + size - 2), 2)
        elif action == 'attack':
            # Épée
            pygame.draw.line(surface, color, (x + 3, y + size - 3), (x + size - 3, y + 3), 2)
            pygame.draw.line(surface, color, (x + size - 6, y + 6), (x + size - 3, y + 9), 2)
        elif action == 'sabotage':
            # Tête diable
            pygame.draw.circle(surface, color, (cx, cy + 2), size // 3, 2)
            pygame.draw.line(surface, color, (cx - 5, cy - 2), (cx - 6, y + 2), 2)
            pygame.draw.line(surface, color, (cx + 5, cy - 2), (cx + 6, y + 2), 2)
        elif action == 'sweep':
            # Balai
            pygame.draw.line(surface, color, (cx, y + 2), (cx, y + size - 6), 2)
            pygame.draw.line(surface, color, (x + 3, y + size - 3), (x + size - 3, y + size - 3), 3)
        elif action == 'inventory':
            # Sac/Inventaire
            pygame.draw.rect(surface, color, (x + 4, y + 5, size - 8, size - 8), 2, border_radius=2)
            pygame.draw.line(surface, color, (x + 7, y + 2), (x + 7, y + 6), 2)
            pygame.draw.line(surface, color, (x + size - 7, y + 2), (x + size - 7, y + 6), 2)
            pygame.draw.line(surface, color, (x + 7, y + 2), (x + size - 7, y + 2), 2)
            
    def _draw_key_button(self, surface, key_name, x, y, color, is_waiting=False):
        """Dessine un bouton de touche avec taille adaptée au texte"""
        if is_waiting:
            text = "..."
            text_color = YELLOW
        else:
            text = key_name
            text_color = color
            
        # Calculer la taille du bouton basée sur le texte
        text_surface = self.key_font.render(text, True, text_color)
        text_width = text_surface.get_width()
        
        # Padding et taille minimum
        padding = 16
        min_width = 50
        btn_width = max(min_width, text_width + padding * 2)
        btn_height = 32
        
        # Dessiner le bouton
        btn_rect = pygame.Rect(x - btn_width, y, btn_width, btn_height)
        
        # Fond du bouton
        pygame.draw.rect(surface, (40, 40, 55), btn_rect, border_radius=6)
        
        if is_waiting:
            # Animation de bordure
            pygame.draw.rect(surface, YELLOW, btn_rect, 2, border_radius=6)
        else:
            pygame.draw.rect(surface, color, btn_rect, 2, border_radius=6)
        
        # Texte centré
        text_rect = text_surface.get_rect(center=btn_rect.center)
        surface.blit(text_surface, text_rect)
        
        return btn_width
        
    def draw(self):
        if not self.visible:
            return
            
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Fond du menu avec dégradé subtil
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(self.screen, (30, 30, 45), menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, MENU_ACCENT, menu_rect, 3, border_radius=15)
        
        # Titre
        title = self.title_font.render("Configuration des Touches", True, WHITE)
        self.screen.blit(title, (self.menu_x + (self.menu_width - title.get_width()) // 2, self.menu_y + 15))
        
        # Tabs joueurs
        tab_y = self.menu_y + 70
        tab_width = (self.menu_width - 60) // 2
        
        for i, player_name in enumerate(["JOUEUR 1", "JOUEUR 2"]):
            tab_x = self.menu_x + 20 + i * (tab_width + 20)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 40)
            
            color = ORANGE if i == 0 else GREEN
            
            if i == self.selected_player:
                pygame.draw.rect(self.screen, color, tab_rect, border_radius=8)
                text_color = BLACK
            else:
                pygame.draw.rect(self.screen, (50, 50, 60), tab_rect, border_radius=8)
                pygame.draw.rect(self.screen, (80, 80, 90), tab_rect, 1, border_radius=8)
                text_color = GRAY
                
            tab_text = self.font.render(player_name, True, text_color)
            self.screen.blit(tab_text, (tab_x + (tab_width - tab_text.get_width()) // 2, tab_y + 10))
            
        # Liste des touches
        list_y = tab_y + 55
        player_key = f'player{self.selected_player + 1}'
        player_color = ORANGE if self.selected_player == 0 else GREEN
        item_height = 42
        
        for i, action in enumerate(self.actions):
            item_y = list_y + i * item_height
            item_rect = pygame.Rect(self.menu_x + 30, item_y, self.menu_width - 60, item_height - 4)
            
            # Highlight si sélectionné
            if i == self.selected_action:
                pygame.draw.rect(self.screen, (50, 50, 70), item_rect, border_radius=6)
                pygame.draw.rect(self.screen, player_color, item_rect, 2, border_radius=6)
                icon_color = player_color
            else:
                icon_color = (150, 150, 160)
                
            # Icône de l'action
            icon_size = 24
            icon_x = item_rect.x + 12
            icon_y = item_y + (item_height - icon_size) // 2 - 2
            self._draw_action_icon(self.screen, action, icon_x, icon_y, icon_size, icon_color)
            
            # Nom de l'action
            action_name = self.key_bindings.get_action_name(action)
            name_text = self.font.render(action_name, True, WHITE if i == self.selected_action else (200, 200, 200))
            self.screen.blit(name_text, (item_rect.x + 45, item_y + 8))
            
            # Touche actuelle (bouton adaptatif)
            current_key = self.key_bindings.get_key(player_key, action)
            key_name = self.key_bindings.get_key_name(current_key)
            
            is_waiting = self.waiting_for_key and i == self.selected_action
            self._draw_key_button(self.screen, key_name, item_rect.right - 15, item_y + 5, player_color, is_waiting)
            
        # Instructions avec icônes dessinées - Positionnées plus bas
        instructions_y = self.menu_y + self.menu_height - 45
        
        # Dessiner les instructions avec des icônes de flèches
        inst_x = self.menu_x + 30
        inst_y = instructions_y
        
        if self.waiting_for_key:
            inst_text = self.small_font.render("Appuyez sur la nouvelle touche  |  ECHAP pour annuler", True, GRAY)
            self.screen.blit(inst_text, (self.menu_x + (self.menu_width - inst_text.get_width()) // 2, inst_y))
            # Warning
            warning = self.small_font.render("(Les touches deja utilisees seront refusees)", True, (180, 100, 100))
            self.screen.blit(warning, (self.menu_x + (self.menu_width - warning.get_width()) // 2, instructions_y + 20))
        else:
            # Dessiner les instructions avec des vraies flèches
            hint_color = (140, 140, 150)
            arrow_size = 14
            
            # Flèches haut/bas pour naviguer
            self._draw_arrow_icon(self.screen, 'up', inst_x, inst_y, arrow_size, hint_color)
            self._draw_arrow_icon(self.screen, 'down', inst_x + 16, inst_y, arrow_size, hint_color)
            nav_text = self.small_font.render("Naviguer", True, hint_color)
            self.screen.blit(nav_text, (inst_x + 35, inst_y))
            
            # Flèches gauche/droite pour changer de joueur
            sep_x = inst_x + 130
            self._draw_arrow_icon(self.screen, 'left', sep_x, inst_y, arrow_size, hint_color)
            self._draw_arrow_icon(self.screen, 'right', sep_x + 16, inst_y, arrow_size, hint_color)
            player_text = self.small_font.render("Joueur", True, hint_color)
            self.screen.blit(player_text, (sep_x + 35, inst_y))
            
            # Autres instructions
            other_inst = self.small_font.render("ENTREE Modifier  |  R Reset  |  ECHAP Fermer", True, hint_color)
            self.screen.blit(other_inst, (inst_x + 250, inst_y))
