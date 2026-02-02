import pygame
from config import *
from rendering.camera import Camera

class SplitScreenRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.width = SCREEN_WIDTH // 2
        self.height = SCREEN_HEIGHT
        
        self.surface1 = pygame.Surface((self.width, self.height))
        self.surface2 = pygame.Surface((self.width, self.height))
        
        self.camera1 = Camera(self.width, self.height)
        self.camera2 = Camera(self.width, self.height)
        
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)
        
    def draw(self, game_state):
        p1 = game_state.players[0]
        p2 = game_state.players[1]
        
        # Get zones for each player
        zone1 = game_state.world_map.get_zone(p1.current_zone)
        zone2 = game_state.world_map.get_zone(p2.current_zone)
        
        # Update cameras
        self.camera1.update(p1, zone1)
        self.camera2.update(p2, zone2)
        
        # Draw P1 View
        self.surface1.fill(DARK_GRAY)
        game_state.draw_zone(self.surface1, self.camera1, p1.current_zone)
        p1.draw(self.surface1, self.camera1)
        
        # Draw P2 View
        self.surface2.fill(DARK_GRAY)
        game_state.draw_zone(self.surface2, self.camera2, p2.current_zone)
        p2.draw(self.surface2, self.camera2)
        
        # Blit to main screen
        self.screen.blit(self.surface1, (0, 0))
        self.screen.blit(self.surface2, (self.width, 0))
        
        # Draw Divider
        pygame.draw.line(self.screen, BORDER_COLOR, (self.width, 0), (self.width, self.height), BORDER_THICKNESS)
        
        # Draw HUD
        self._draw_hud(game_state, p1, p2)
        
        # Draw game over screen if needed
        if game_state.game_over:
            self._draw_game_over(game_state)
        
    def _draw_hud(self, game_state, p1, p2):
        # Timer at center top
        remaining = game_state.get_remaining_time()
        minutes = remaining // 60
        seconds = remaining % 60
        timer_text = self.big_font.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        
        # Timer background
        bg_rect = timer_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, BLACK, bg_rect, border_radius=5)
        self.screen.blit(timer_text, timer_rect)
        
        # P1 HUD (left)
        self._draw_player_hud(10, 50, p1, "TACOS", ORANGE)
        
        # P2 HUD (right)
        self._draw_player_hud(self.width + 10, 50, p2, "KEBAB", GREEN)
        
    def _draw_player_hud(self, x, y, player, resto_name, color):
        # Background panel
        panel_rect = pygame.Rect(x, y, 200, 80)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, color, panel_rect, 2, border_radius=8)
        
        # Restaurant name
        name_text = self.small_font.render(resto_name, True, color)
        self.screen.blit(name_text, (x + 10, y + 5))
        
        # Money
        money_text = self.font.render(f"${player.money}", True, (255, 215, 0))
        self.screen.blit(money_text, (x + 10, y + 25))
        
        # Reputation bar
        rep_label = self.small_font.render("Rep:", True, WHITE)
        self.screen.blit(rep_label, (x + 10, y + 55))
        
        # Rep bar background
        bar_x = x + 50
        bar_width = 130
        pygame.draw.rect(self.screen, GRAY, (bar_x, y + 57, bar_width, 15), border_radius=3)
        
        # Rep bar fill
        fill_width = int(bar_width * player.reputation / 100)
        rep_color = GREEN if player.reputation > 50 else ORANGE if player.reputation > 25 else RED
        pygame.draw.rect(self.screen, rep_color, (bar_x, y + 57, fill_width, 15), border_radius=3)
        
        # Rep text
        rep_text = self.small_font.render(f"{player.reputation}%", True, WHITE)
        self.screen.blit(rep_text, (bar_x + bar_width // 2 - 15, y + 55))
        
        # Zone indicator
        zone_text = self.small_font.render(f"[{player.current_zone.upper()}]", True, (150, 150, 150))
        self.screen.blit(zone_text, (x + 120, y + 5))
        
    def _draw_game_over(self, game_state):
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        go_font = pygame.font.SysFont(None, 72)
        go_text = go_font.render("FIN DE PARTIE!", True, WHITE)
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(go_text, go_rect)
        
        # Winner
        winner = game_state.get_winner()
        p1 = game_state.players[0]
        p2 = game_state.players[1]
        
        if winner == 1:
            winner_text = "JOUEUR 1 (TACOS) GAGNE!"
            winner_color = ORANGE
        elif winner == 2:
            winner_text = "JOUEUR 2 (KEBAB) GAGNE!"
            winner_color = GREEN
        else:
            winner_text = "ÉGALITÉ!"
            winner_color = WHITE
            
        win_render = self.big_font.render(winner_text, True, winner_color)
        win_rect = win_render.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(win_render, win_rect)
        
        # Scores
        score_text = self.font.render(f"Tacos: ${p1.money}  |  Kebab: ${p2.money}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(score_text, score_rect)
        
        # Restart hint
        hint_text = self.small_font.render("Appuyez sur ESPACE pour rejouer ou ÉCHAP pour quitter", True, GRAY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint_text, hint_rect)
