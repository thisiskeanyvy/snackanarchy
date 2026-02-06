"""
Menu d'historique - Affiche les statistiques et l'historique des parties
"""
import pygame
import math
import time
from config import *
from game.history import GameHistory


class HistoryMenu:
    """Affiche l'historique des parties et les statistiques"""
    
    TAB_HISTORY = 0
    TAB_LEADERBOARD = 1
    TAB_STATS = 2
    
    def __init__(self, screen):
        self.screen = screen
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.visible = False
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.normal_font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        
        # Navigation
        self.current_tab = self.TAB_HISTORY
        self.scroll_offset = 0
        self.selected_player = None  # Pour les stats détaillées
        
        # Colors
        self.bg_color = (25, 25, 35)
        self.panel_color = (35, 35, 50)
        self.accent_color = (255, 140, 0)
        self.highlight_color = (255, 200, 100)
        self.win_color = (76, 175, 80)
        self.lose_color = (200, 80, 80)
        
        # Animation
        self.start_time = time.time()
        
        # Tabs
        self.tabs = ["Historique", "Classement", "Statistiques"]
        
        # History reference
        self.history = GameHistory.get()
    
    def _draw_medal(self, x, y, rank, color):
        """Dessine une médaille pour le classement"""
        # Cercle de la médaille
        cx, cy = x + 15, y + 15
        pygame.draw.circle(self.screen, color, (cx, cy), 12, 0)
        pygame.draw.circle(self.screen, (50, 50, 60), (cx, cy), 12, 2)
        
        # Numéro au centre
        num_text = self.normal_font.render(str(rank), True, (30, 30, 40))
        num_rect = num_text.get_rect(center=(cx, cy))
        self.screen.blit(num_text, num_rect)
        
        # Ruban
        pygame.draw.polygon(self.screen, color, [
            (cx - 6, cy + 10),
            (cx - 10, cy + 20),
            (cx - 2, cy + 16)
        ])
        pygame.draw.polygon(self.screen, color, [
            (cx + 6, cy + 10),
            (cx + 10, cy + 20),
            (cx + 2, cy + 16)
        ])
    
    def _draw_stat_icon(self, x, y, icon_type, color):
        """Dessine une icône pour les statistiques"""
        size = 30
        
        if icon_type == "gamepad":
            # Manette
            pygame.draw.rect(self.screen, color, (x + 4, y + 8, size - 8, size - 16), 2, border_radius=4)
            pygame.draw.circle(self.screen, color, (x + size // 3, y + size // 2), 3)
            pygame.draw.circle(self.screen, color, (x + 2 * size // 3, y + size // 2), 3)
        elif icon_type == "money":
            # Pièce avec €
            pygame.draw.circle(self.screen, color, (x + size // 2, y + size // 2), size // 2 - 2, 2)
            dollar = self.normal_font.render("€", True, color)
            self.screen.blit(dollar, dollar.get_rect(center=(x + size // 2, y + size // 2)))
        elif icon_type == "clients":
            # Silhouettes
            for i, offset in enumerate([-7, 0, 7]):
                pygame.draw.circle(self.screen, color, (x + size // 2 + offset, y + 8), 4)
                pygame.draw.line(self.screen, color, (x + size // 2 + offset, y + 12), 
                               (x + size // 2 + offset, y + size - 6), 2)
        elif icon_type == "tacos":
            # Forme de tacos (demi-cercle)
            pygame.draw.arc(self.screen, color, (x + 2, y + 4, size - 4, size - 8), 0, 3.14, 3)
            pygame.draw.line(self.screen, color, (x + 2, y + size // 2), (x + size - 2, y + size // 2), 2)
        elif icon_type == "kebab":
            # Broche
            pygame.draw.line(self.screen, color, (x + size // 2, y + 2), (x + size // 2, y + size - 2), 2)
            for i in range(3):
                pygame.draw.ellipse(self.screen, color, (x + 6, y + 6 + i * 8, size - 12, 7), 2)
        elif icon_type == "target":
            # Cible
            cx, cy = x + size // 2, y + size // 2
            for r in [12, 8, 4]:
                pygame.draw.circle(self.screen, color, (cx, cy), r, 2 if r > 4 else 0)
    
    def toggle(self):
        """Ouvre/ferme le menu"""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
            self.current_tab = self.TAB_HISTORY
            self.start_time = time.time()
    
    def close(self):
        """Ferme le menu"""
        self.visible = False
    
    def handle_input(self, event):
        """Gère les entrées utilisateur"""
        if not self.visible:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return "close"
            
            # Navigation entre les onglets
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.current_tab = (self.current_tab - 1) % len(self.tabs)
                self.scroll_offset = 0
                return "navigate"
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.current_tab = (self.current_tab + 1) % len(self.tabs)
                self.scroll_offset = 0
                return "navigate"
            
            # Scroll
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll_offset = max(0, self.scroll_offset - 1)
                return "scroll"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll_offset += 1
                return "scroll"
        
        # Support souris
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                return self._handle_mouse_click(event.pos)
            elif event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Scroll down
                self.scroll_offset += 1
        
        return None
    
    def _handle_mouse_click(self, pos):
        """Gère les clics souris"""
        # Vérifier les onglets
        tab_width = 200
        tab_y = 80
        tab_height = 40
        start_x = (self.width - len(self.tabs) * tab_width) // 2
        
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(start_x + i * tab_width, tab_y, tab_width - 10, tab_height)
            if tab_rect.collidepoint(pos):
                self.current_tab = i
                self.scroll_offset = 0
                return "navigate"
        
        # Bouton fermer
        close_rect = pygame.Rect(self.width - 60, 20, 40, 40)
        if close_rect.collidepoint(pos):
            self.close()
            return "close"
        
        return None
    
    def draw(self):
        """Dessine le menu d'historique"""
        if not self.visible:
            return
        
        elapsed = time.time() - self.start_time
        
        # Overlay semi-transparent
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Titre
        title = self.title_font.render("HISTORIQUE", True, self.accent_color)
        y_offset = math.sin(elapsed * 2) * 2
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 40 + y_offset)))
        
        # Bouton fermer
        self._draw_close_button()
        
        # Onglets
        self._draw_tabs()
        
        # Contenu selon l'onglet
        content_rect = pygame.Rect(50, 140, self.width - 100, self.height - 200)
        pygame.draw.rect(self.screen, self.panel_color, content_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.accent_color, content_rect, 2, border_radius=10)
        
        if self.current_tab == self.TAB_HISTORY:
            self._draw_history_tab(content_rect)
        elif self.current_tab == self.TAB_LEADERBOARD:
            self._draw_leaderboard_tab(content_rect)
        elif self.current_tab == self.TAB_STATS:
            self._draw_stats_tab(content_rect)
        
        # Instructions
        hint = "←→ Changer d'onglet  |  ↑↓ Défiler  |  ÉCHAP Fermer"
        hint_surface = self.small_font.render(hint, True, (100, 100, 120))
        self.screen.blit(hint_surface, hint_surface.get_rect(center=(self.width // 2, self.height - 25)))
    
    def _draw_close_button(self):
        """Dessine le bouton fermer"""
        close_rect = pygame.Rect(self.width - 60, 20, 40, 40)
        pygame.draw.rect(self.screen, (80, 40, 40), close_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 80, 80), close_rect, 2, border_radius=8)
        
        x_text = self.header_font.render("×", True, WHITE)
        self.screen.blit(x_text, x_text.get_rect(center=close_rect.center))
    
    def _draw_tabs(self):
        """Dessine les onglets"""
        tab_width = 200
        tab_height = 40
        start_x = (self.width - len(self.tabs) * tab_width) // 2
        tab_y = 80
        
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(start_x + i * tab_width, tab_y, tab_width - 10, tab_height)
            
            if i == self.current_tab:
                pygame.draw.rect(self.screen, self.accent_color, tab_rect, border_radius=8)
                text_color = BLACK
            else:
                pygame.draw.rect(self.screen, self.panel_color, tab_rect, border_radius=8)
                pygame.draw.rect(self.screen, (80, 80, 100), tab_rect, 2, border_radius=8)
                text_color = (150, 150, 150)
            
            text = self.normal_font.render(tab, True, text_color)
            self.screen.blit(text, text.get_rect(center=tab_rect.center))
    
    def _draw_history_tab(self, content_rect):
        """Dessine l'onglet historique des parties"""
        games = self.history.get_recent_games(20)
        
        if not games:
            no_data = self.normal_font.render("Aucune partie enregistrée", True, (150, 150, 150))
            self.screen.blit(no_data, no_data.get_rect(center=content_rect.center))
            return
        
        # En-tête
        headers = ["Date", "Joueur 1", "Score", "VS", "Joueur 2", "Score", "Durée"]
        header_x = [70, 200, 350, 430, 500, 650, 780]
        
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, self.accent_color)
            self.screen.blit(text, (header_x[i], content_rect.y + 15))
        
        # Ligne séparatrice
        pygame.draw.line(self.screen, (80, 80, 100), 
                        (content_rect.x + 10, content_rect.y + 45),
                        (content_rect.right - 10, content_rect.y + 45), 2)
        
        # Parties
        y = content_rect.y + 55
        row_height = 45
        visible_games = games[self.scroll_offset:self.scroll_offset + 10]
        
        for game in visible_games:
            if y + row_height > content_rect.bottom - 10:
                break
            
            # Date
            date_str = game['date'][:10]  # YYYY-MM-DD
            date_text = self.small_font.render(date_str, True, (180, 180, 180))
            self.screen.blit(date_text, (70, y + 10))
            
            # Joueurs
            p1 = game['players'][0] if len(game['players']) > 0 else {}
            p2 = game['players'][1] if len(game['players']) > 1 else {}
            
            p1_color = self.win_color if p1.get('is_winner') else (180, 180, 180)
            p2_color = self.win_color if p2.get('is_winner') else (180, 180, 180)
            
            p1_name = self.small_font.render(p1.get('name', 'Joueur 1')[:12], True, p1_color)
            p1_score = self.small_font.render(f"{p1.get('money', 0)} €", True, p1_color)
            self.screen.blit(p1_name, (200, y + 10))
            self.screen.blit(p1_score, (350, y + 10))
            
            vs = self.small_font.render("VS", True, (100, 100, 100))
            self.screen.blit(vs, (430, y + 10))
            
            p2_name = self.small_font.render(p2.get('name', 'Joueur 2')[:12], True, p2_color)
            p2_score = self.small_font.render(f"{p2.get('money', 0)} €", True, p2_color)
            self.screen.blit(p2_name, (500, y + 10))
            self.screen.blit(p2_score, (650, y + 10))
            
            # Durée
            duration = game.get('duration', 0)
            duration_text = self.small_font.render(f"{duration // 60}min", True, (150, 150, 150))
            self.screen.blit(duration_text, (780, y + 10))
            
            y += row_height
        
        # Indicateur de scroll
        if len(games) > 10:
            scroll_text = self.small_font.render(
                f"Page {self.scroll_offset // 10 + 1}/{(len(games) - 1) // 10 + 1}", 
                True, (100, 100, 100)
            )
            self.screen.blit(scroll_text, scroll_text.get_rect(
                center=(content_rect.centerx, content_rect.bottom - 20)
            ))
    
    def _draw_leaderboard_tab(self, content_rect):
        """Dessine l'onglet classement"""
        leaderboard = self.history.get_leaderboard('wins')
        
        if not leaderboard:
            no_data = self.normal_font.render("Aucun joueur enregistré", True, (150, 150, 150))
            self.screen.blit(no_data, no_data.get_rect(center=content_rect.center))
            return
        
        # En-tête
        headers = ["Rang", "Joueur", "Victoires", "Défaites", "Parties", "Total €"]
        header_x = [70, 150, 350, 470, 590, 710]
        
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, self.accent_color)
            self.screen.blit(text, (header_x[i], content_rect.y + 15))
        
        pygame.draw.line(self.screen, (80, 80, 100), 
                        (content_rect.x + 10, content_rect.y + 45),
                        (content_rect.right - 10, content_rect.y + 45), 2)
        
        # Classement
        y = content_rect.y + 55
        row_height = 40
        
        for rank, player in enumerate(leaderboard[self.scroll_offset:self.scroll_offset + 12], 
                                       start=self.scroll_offset + 1):
            if y + row_height > content_rect.bottom - 10:
                break
            
            # Couleur selon le rang
            if rank == 1:
                color = (255, 215, 0)  # Or
            elif rank == 2:
                color = (192, 192, 192)  # Argent
            elif rank == 3:
                color = (205, 127, 50)  # Bronze
            else:
                color = (180, 180, 180)
            
            # Dessiner médaille ou numéro
            if rank <= 3:
                self._draw_medal(70, y + 5, rank, color)
            else:
                rank_text = self.normal_font.render(f"#{rank}", True, color)
                self.screen.blit(rank_text, (70, y + 5))
            
            name_text = self.normal_font.render(player['name'][:15], True, color)
            self.screen.blit(name_text, (150, y + 5))
            
            wins_text = self.normal_font.render(str(player['wins']), True, self.win_color)
            self.screen.blit(wins_text, (380, y + 5))
            
            losses_text = self.normal_font.render(str(player['losses']), True, self.lose_color)
            self.screen.blit(losses_text, (500, y + 5))
            
            games_text = self.normal_font.render(str(player['games_played']), True, (150, 150, 150))
            self.screen.blit(games_text, (610, y + 5))
            
            money_text = self.normal_font.render(f"{player['total_money']} €", True, (255, 215, 0))
            self.screen.blit(money_text, (710, y + 5))
            
            y += row_height
    
    def _draw_stats_tab(self, content_rect):
        """Dessine l'onglet statistiques globales"""
        all_stats = self.history.get_all_player_stats()
        
        if not all_stats:
            no_data = self.normal_font.render("Aucune statistique disponible", True, (150, 150, 150))
            self.screen.blit(no_data, no_data.get_rect(center=content_rect.center))
            return
        
        # Statistiques globales
        total_games = sum(s['games_played'] for s in all_stats.values()) // 2  # /2 car 2 joueurs par partie
        total_money = sum(s['total_money'] for s in all_stats.values())
        total_clients = sum(s['total_clients_served'] for s in all_stats.values())
        total_tacos = sum(s['total_tacos'] for s in all_stats.values())
        total_kebabs = sum(s['total_kebabs'] for s in all_stats.values())
        
        # Affichage en grille avec icônes dessinées
        stats_items = [
            ("Parties jouees", str(total_games), "gamepad"),
            ("Argent total gagne", f"{total_money} €", "money"),
            ("Clients servis", str(total_clients), "clients"),
            ("Tacos vendus", str(total_tacos), "tacos"),
            ("Kebabs vendus", str(total_kebabs), "kebab"),
            ("Joueurs uniques", str(len(all_stats)), "target"),
        ]
        
        card_width = 350
        card_height = 80
        cards_per_row = 2
        start_x = content_rect.x + 50
        start_y = content_rect.y + 30
        
        for i, (label, value, icon_type) in enumerate(stats_items):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + 30)
            y = start_y + row * (card_height + 20)
            
            card_rect = pygame.Rect(x, y, card_width, card_height)
            pygame.draw.rect(self.screen, (45, 45, 60), card_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.accent_color, card_rect, 2, border_radius=8)
            
            # Icône dessinée
            self._draw_stat_icon(x + 15, y + 22, icon_type, self.accent_color)
            
            label_text = self.small_font.render(label, True, (150, 150, 150))
            self.screen.blit(label_text, (x + 55, y + 15))
            
            value_text = self.header_font.render(value, True, self.highlight_color)
            self.screen.blit(value_text, (x + 55, y + 40))
        
        # Records
        if all_stats:
            y_records = start_y + 3 * (card_height + 20) + 20
            records_title = self.header_font.render("Records", True, self.accent_color)
            self.screen.blit(records_title, (start_x, y_records))
            
            pygame.draw.line(self.screen, (80, 80, 100),
                            (start_x, y_records + 35),
                            (content_rect.right - 50, y_records + 35), 2)
            
            # Trouver les records
            best_money_player = max(all_stats.items(), key=lambda x: x[1]['best_money'])
            most_wins_player = max(all_stats.items(), key=lambda x: x[1]['wins'])
            
            records = [
                (f"Plus gros gain: {best_money_player[1]['best_money']} €", best_money_player[0]),
                (f"Plus de victoires: {most_wins_player[1]['wins']}", most_wins_player[0]),
            ]
            
            y = y_records + 50
            for record_text, player_name in records:
                text = self.normal_font.render(f"{record_text} - {player_name}", True, (200, 200, 200))
                self.screen.blit(text, (start_x, y))
                y += 30
