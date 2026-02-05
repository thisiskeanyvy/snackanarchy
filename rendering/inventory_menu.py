"""
Menu d'inventaire pour afficher le stock de nourriture et les équipements
"""
import pygame
from config import *

class InventoryMenu:
    """Gestionnaire des inventaires pour les deux joueurs"""
    
    def __init__(self, screen):
        self.screen = screen
        
        # Deux inventaires séparés, un pour chaque joueur
        self.player_menus = [
            PlayerInventoryMenu(screen, 0),  # Joueur 1 (gauche)
            PlayerInventoryMenu(screen, 1),  # Joueur 2 (droite)
        ]
        
    @property
    def visible(self):
        """Retourne True si au moins un inventaire est ouvert"""
        return any(menu.visible for menu in self.player_menus)
    
    def is_visible_for(self, player_idx):
        """Vérifie si l'inventaire est ouvert pour un joueur spécifique"""
        return self.player_menus[player_idx].visible
        
    def toggle(self, player_idx):
        """Ouvre/ferme l'inventaire pour un joueur"""
        self.player_menus[player_idx].toggle()
            
    def close(self, player_idx=None):
        """Ferme l'inventaire d'un joueur ou tous les inventaires"""
        if player_idx is not None:
            self.player_menus[player_idx].close()
        else:
            for menu in self.player_menus:
                menu.close()
        
    def handle_input(self, event, game_state):
        """Gère les inputs pour les deux inventaires"""
        results = []
        for menu in self.player_menus:
            if menu.visible:
                result = menu.handle_input(event, game_state)
                if result:
                    results.append((menu.player_idx, result))
        
        # Retourner le premier résultat significatif
        for player_idx, result in results:
            if result:
                return result
        return None
        
    def draw(self, game_state):
        """Dessine les inventaires ouverts"""
        for menu in self.player_menus:
            if menu.visible:
                menu.draw(game_state)


class PlayerInventoryMenu:
    """Menu d'inventaire pour un joueur spécifique"""
    
    def __init__(self, screen, player_idx):
        self.screen = screen
        self.player_idx = player_idx
        self.visible = False
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 36)
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Position du menu (sur la moitié d'écran du joueur)
        self.menu_width = 350
        self.menu_height = 450
        
        # Calcul de la position selon le joueur
        half_screen = SCREEN_WIDTH // 2
        if player_idx == 0:
            # Joueur 1: moitié gauche
            self.menu_x = (half_screen - self.menu_width) // 2
        else:
            # Joueur 2: moitié droite
            self.menu_x = half_screen + (half_screen - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        
        # Tab sélectionné
        self.current_tab = 0  # 0 = Stock, 1 = Équipement, 2 = Missions, 3 = Sabotages
        self.tabs = ["Stock", "Equipement", "Missions", "Sabotages"]
        
        # Scroll
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Sélection pour réappro
        self.selected_ingredient = 0
    
    def _draw_arrow_icon(self, surface, direction, x, y, size, color):
        """Flèche directionnelle dessinée (sans emoji)."""
        cx, cy = x + size // 2, y + size // 2
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
    
    def _draw_check_icon(self, surface, x, y, size, color):
        """Coche dessinée (OK / validé)."""
        pygame.draw.line(surface, color, (x + 2, y + size // 2), (x + size // 3, y + size - 3), 2)
        pygame.draw.line(surface, color, (x + size // 3, y + size - 3), (x + size - 2, y + 2), 2)
    
    def _draw_cross_icon(self, surface, x, y, size, color):
        """Croix dessinée (erreur / indisponible)."""
        pygame.draw.line(surface, color, (x + 2, y + 2), (x + size - 2, y + size - 2), 2)
        pygame.draw.line(surface, color, (x + size - 2, y + 2), (x + 2, y + size - 2), 2)
    
    def _draw_weapon_icon(self, surface, x, y, size, color):
        """Petite icône couteau/arme dessinée."""
        cx = x + size // 2
        pygame.draw.line(surface, color, (x + 2, y + size - 2), (cx + 2, y + 2), 2)
        pygame.draw.line(surface, color, (cx + 2, y + 2), (x + size - 2, y + size - 4), 2)
        
    def toggle(self):
        """Ouvre/ferme l'inventaire"""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
            self.selected_ingredient = 0
            
    def close(self):
        self.visible = False
        
    def handle_input(self, event, game_state):
        """Gère les inputs dans le menu d'inventaire"""
        if not self.visible:
            return None
        
        # Touches spécifiques selon le joueur
        if self.player_idx == 0:
            # Joueur 1: ZQSD + E + Tab/I
            key_up = pygame.K_w
            key_down = pygame.K_s
            key_left = pygame.K_a
            key_right = pygame.K_d
            key_action = pygame.K_e
            key_close = [pygame.K_ESCAPE, pygame.K_i, pygame.K_TAB]
        else:
            # Joueur 2: Flèches + Entrée + L
            key_up = pygame.K_UP
            key_down = pygame.K_DOWN
            key_left = pygame.K_LEFT
            key_right = pygame.K_RIGHT
            key_action = pygame.K_RETURN
            key_close = [pygame.K_ESCAPE, pygame.K_l, pygame.K_RSHIFT]
            
        if event.type == pygame.KEYDOWN:
            # Fermer le menu
            if event.key in key_close:
                self.close()
                return "close"
                
            # Navigation tabs
            if event.key == key_left:
                self.current_tab = (self.current_tab - 1) % len(self.tabs)
                self.scroll_offset = 0
                self.selected_ingredient = 0
                return "navigate"
                
            if event.key == key_right:
                self.current_tab = (self.current_tab + 1) % len(self.tabs)
                self.scroll_offset = 0
                self.selected_ingredient = 0
                return "navigate"
                
            # Navigation verticale dans le stock
            if self.current_tab == 0:
                player = game_state.players[self.player_idx]
                ingredients = list(player.food_stock.ingredients.keys())
                
                if event.key == key_up:
                    self.selected_ingredient = max(0, self.selected_ingredient - 1)
                    return "navigate"
                    
                if event.key == key_down:
                    self.selected_ingredient = min(len(ingredients) - 1, self.selected_ingredient + 1)
                    return "navigate"
                    
                # Réapprovisionner l'ingrédient sélectionné
                if event.key == key_action:
                    if ingredients:
                        ing_name = ingredients[self.selected_ingredient]
                        amount, cost = player.restock(ing_name)
                        if amount > 0:
                            return f"restock_{ing_name}"
                    return None
                    
            # Missions (onglet 2) - juste navigation, pas d'action
            if self.current_tab == 2:
                player = game_state.players[self.player_idx]
                if hasattr(player, 'mission_manager'):
                    missions = player.mission_manager.get_active_missions()
                    
                    if event.key == key_up:
                        self.selected_ingredient = max(0, self.selected_ingredient - 1)
                        return "navigate"
                        
                    if event.key == key_down:
                        self.selected_ingredient = min(len(missions) - 1, self.selected_ingredient + 1)
                        return "navigate"
            
            # Sabotages (onglet 3)
            if self.current_tab == 3:
                sabotages = game_state.get_available_sabotages(self.player_idx)
                
                if event.key == key_up:
                    self.selected_ingredient = max(0, self.selected_ingredient - 1)
                    return "navigate"
                    
                if event.key == key_down:
                    self.selected_ingredient = min(len(sabotages) - 1, self.selected_ingredient + 1)
                    return "navigate"
                    
                # Exécuter le sabotage sélectionné
                if event.key == key_action:
                    if sabotages and self.selected_ingredient < len(sabotages):
                        sabotage = sabotages[self.selected_ingredient]
                        if sabotage['cooldown'] <= 0:
                            success, msg = game_state.handle_sabotage(self.player_idx, sabotage['name'])
                            if success:
                                self.close()
                                return f"sabotage_{sabotage['name']}"
                    return None
                    
        return None
        
    def draw(self, game_state):
        """Dessine le menu d'inventaire"""
        if not self.visible:
            return
            
        player = game_state.players[self.player_idx]
        
        # Overlay semi-transparent uniquement sur la moitié d'écran du joueur
        half_screen = SCREEN_WIDTH // 2
        if self.player_idx == 0:
            overlay_x = 0
        else:
            overlay_x = half_screen
        
        overlay = pygame.Surface((half_screen, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (overlay_x, 0))
        
        # Fond du menu
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(self.screen, (30, 30, 40), menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, MENU_ACCENT, menu_rect, 3, border_radius=15)
        
        # Titre
        title_color = ORANGE if self.player_idx == 0 else GREEN
        title = self.title_font.render(f"Inventaire - {player.username}", True, title_color)
        self.screen.blit(title, (self.menu_x + 15, self.menu_y + 12))
        
        # Argent disponible
        money_text = self.font.render(f"${player.money}", True, YELLOW)
        self.screen.blit(money_text, (self.menu_x + self.menu_width - 80, self.menu_y + 15))
        
        # Tabs
        tab_y = self.menu_y + 50
        tab_width = (self.menu_width - 30) // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_x = self.menu_x + 15 + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width - 5, 30)
            
            if i == self.current_tab:
                pygame.draw.rect(self.screen, MENU_ACCENT, tab_rect, border_radius=5)
                text_color = BLACK
            else:
                pygame.draw.rect(self.screen, (50, 50, 60), tab_rect, border_radius=5)
                pygame.draw.rect(self.screen, (80, 80, 90), tab_rect, 1, border_radius=5)
                text_color = WHITE
                
            tab_text = self.small_font.render(tab, True, text_color)
            text_x = tab_x + (tab_width - 5 - tab_text.get_width()) // 2
            self.screen.blit(tab_text, (text_x, tab_y + 6))
            
        # Contenu selon le tab
        content_y = tab_y + 40
        content_height = self.menu_height - 120
        
        if self.current_tab == 0:
            self._draw_stock_tab(player, content_y, content_height)
        elif self.current_tab == 1:
            self._draw_equipment_tab(player, content_y, content_height)
        elif self.current_tab == 2:
            self._draw_missions_tab(player, content_y, content_height)
        else:
            self._draw_sabotage_tab(game_state, content_y, content_height)
            
        # Instructions en bas (icônes flèches dessinées pour J2, pas d'emoji)
        inst_y = self.menu_y + self.menu_height - 25
        inst_x = self.menu_x + 15
        arrow_sz = 10
        arrow_color = GRAY
        if self.player_idx == 0:
            inst_text = self.small_font.render("WS Nav | AD Tabs | E Select | I/Tab Fermer", True, GRAY)
            self.screen.blit(inst_text, (inst_x, inst_y))
        else:
            self._draw_arrow_icon(self.screen, 'up', inst_x, inst_y + 2, arrow_sz, arrow_color)
            self._draw_arrow_icon(self.screen, 'down', inst_x + arrow_sz + 2, inst_y + 2, arrow_sz, arrow_color)
            nav_text = self.small_font.render(" Nav | ", True, GRAY)
            self.screen.blit(nav_text, (inst_x + arrow_sz * 2 + 6, inst_y))
            xx = inst_x + arrow_sz * 2 + 6 + nav_text.get_width()
            self._draw_arrow_icon(self.screen, 'left', xx, inst_y + 2, arrow_sz, arrow_color)
            self._draw_arrow_icon(self.screen, 'right', xx + arrow_sz + 2, inst_y + 2, arrow_sz, arrow_color)
            rest = self.small_font.render(" Tabs | Entree Select | L Fermer", True, GRAY)
            self.screen.blit(rest, (xx + arrow_sz * 2 + 6, inst_y))
        
    def _draw_stock_tab(self, player, start_y, height):
        """Dessine l'onglet du stock"""
        x = self.menu_x + 15
        y = start_y
        
        ingredients = list(player.food_stock.ingredients.items())
        
        for i, (name, data) in enumerate(ingredients):
            if y > self.menu_y + self.menu_height - 50:
                break
                
            # Highlight si sélectionné
            item_rect = pygame.Rect(x - 3, y - 2, self.menu_width - 30, 30)
            if i == self.selected_ingredient:
                pygame.draw.rect(self.screen, (60, 60, 80), item_rect, border_radius=5)
                pygame.draw.rect(self.screen, MENU_ACCENT, item_rect, 2, border_radius=5)
                
            # Nom de l'ingrédient (traduit)
            display_name = self._translate_ingredient(name)
            name_text = self.small_font.render(display_name, True, WHITE)
            self.screen.blit(name_text, (x, y + 2))
            
            # Barre de stock
            bar_x = x + 120
            bar_width = 100
            bar_height = 14
            
            # Fond
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, y + 5, bar_width, bar_height), border_radius=3)
            
            # Remplissage
            fill_pct = data['quantity'] / data['max']
            fill_width = int(bar_width * fill_pct)
            
            if fill_pct > 0.5:
                fill_color = GREEN
            elif fill_pct > 0.2:
                fill_color = ORANGE
            else:
                fill_color = RED
                
            if fill_width > 0:
                pygame.draw.rect(self.screen, fill_color, (bar_x, y + 5, fill_width, bar_height), border_radius=3)
                
            # Texte quantité
            qty_text = self.small_font.render(f"{data['quantity']}/{data['max']}", True, WHITE)
            self.screen.blit(qty_text, (bar_x + bar_width + 5, y + 3))
                    
            y += 32
            
        # Prix réappro si sélectionné
        if self.selected_ingredient < len(ingredients):
            name, data = ingredients[self.selected_ingredient]
            needed = data['max'] - data['quantity']
            cost = int(needed * data['price'])
            if needed > 0:
                restock_text = self.small_font.render(f"Réappro: ${cost}", True, YELLOW)
                self.screen.blit(restock_text, (x, y + 5))
            
        # Status broche (icône dessinée, pas d'emoji)
        y += 25
        icon_sz = 14
        if player.food_stock.is_spit_available():
            self._draw_check_icon(self.screen, x, y, icon_sz, GREEN)
            spit_text = self.small_font.render("Broche: OK", True, GREEN)
            self.screen.blit(spit_text, (x + icon_sz + 4, y - 1))
        else:
            self._draw_cross_icon(self.screen, x, y, icon_sz, RED)
            cooldown = int(player.food_stock.get_spit_cooldown())
            spit_text = self.small_font.render(f"Broche volee! ({cooldown}s)", True, RED)
            self.screen.blit(spit_text, (x + icon_sz + 4, y - 1))
        
    def _draw_equipment_tab(self, player, start_y, height):
        """Dessine l'onglet des équipements"""
        x = self.menu_x + 15
        y = start_y
        
        equipment_names = {
            'fryer': 'Friteuse',
            'spit': 'Broche',
            'menu': 'Menu',
            'register': 'Caisse',
            'toilets': 'Toilettes'
        }
        
        for eq_key, eq in player.equipment.items():
            name = equipment_names.get(eq_key, eq_key)
            status = eq.get_status()
            
            # Couleur selon status (icône coche/croix dessinée)
            if status == "OK":
                status_color = GREEN
                self._draw_check_icon(self.screen, x + 125, y - 1, 14, GREEN)
            else:
                status_color = RED
                self._draw_cross_icon(self.screen, x + 125, y - 1, 14, RED)
                
            # Ligne équipement
            eq_text = self.small_font.render(name, True, WHITE)
            self.screen.blit(eq_text, (x, y))
            
            status_text = self.small_font.render(status, True, status_color)
            self.screen.blit(status_text, (x + 144, y))
            
            # Description (tronquée si trop longue)
            desc = eq.description[:35] + "..." if len(eq.description) > 35 else eq.description
            desc_text = self.small_font.render(desc, True, GRAY)
            self.screen.blit(desc_text, (x + 10, y + 18))
            
            y += 42
            
        # Arme équipée (icône couteau dessinée)
        y += 5
        self._draw_weapon_icon(self.screen, x, y - 2, 16, RED if player.get_weapon_info() else GRAY)
        weapon_info = player.get_weapon_info()
        if weapon_info:
            weapon_text = self.small_font.render(f"Arme: {weapon_info['name']} ({weapon_info['uses']})", True, RED)
        else:
            weapon_text = self.small_font.render("Arme: Aucune", True, GRAY)
        self.screen.blit(weapon_text, (x + 22, y))
        
    def _draw_missions_tab(self, player, start_y, height):
        """Dessine l'onglet des missions"""
        x = self.menu_x + 15
        y = start_y
        
        if not hasattr(player, 'mission_manager'):
            no_missions = self.small_font.render("Pas de missions", True, GRAY)
            self.screen.blit(no_missions, (x, y))
            return
            
        missions = player.mission_manager.get_active_missions()
        
        if not missions:
            no_missions = self.small_font.render("Aucune mission active", True, GRAY)
            self.screen.blit(no_missions, (x, y))
            return
        
        # Titre section
        title_text = self.font.render("Missions actives", True, MENU_ACCENT)
        self.screen.blit(title_text, (x, y))
        y += 30
        
        for i, mission in enumerate(missions):
            if y > self.menu_y + self.menu_height - 80:
                break
                
            # Highlight si sélectionné
            item_rect = pygame.Rect(x - 3, y - 2, self.menu_width - 30, 68)
            if i == self.selected_ingredient:
                pygame.draw.rect(self.screen, (60, 60, 80), item_rect, border_radius=5)
                if mission.completed:
                    pygame.draw.rect(self.screen, GREEN, item_rect, 2, border_radius=5)
                else:
                    pygame.draw.rect(self.screen, MENU_ACCENT, item_rect, 2, border_radius=5)
            
            # Nom de la mission
            name_color = GREEN if mission.completed else WHITE
            name_text = self.small_font.render(mission.name, True, name_color)
            self.screen.blit(name_text, (x, y))
            
            # Mini description (objectif)
            desc = mission.description[:42] + "..." if len(mission.description) > 42 else mission.description
            desc_text = self.small_font.render(desc, True, GRAY)
            self.screen.blit(desc_text, (x + 2, y + 16))
            
            # Récompense
            reward_text = self.small_font.render(f"+{mission.reward_money}e", True, YELLOW)
            self.screen.blit(reward_text, (x + 200, y))
            
            if mission.reward_reputation > 0:
                rep_text = self.small_font.render(f"+{mission.reward_reputation}%", True, GREEN)
                self.screen.blit(rep_text, (x + 260, y))
            
            # Barre de progression
            bar_x = x
            bar_y = y + 32
            bar_width = 180
            bar_height = 12
            
            # Fond
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            
            # Remplissage
            progress_ratio = min(1.0, mission.progress / mission.target)
            fill_width = int(bar_width * progress_ratio)
            
            if mission.completed:
                fill_color = GREEN
            else:
                fill_color = MENU_ACCENT
                
            if fill_width > 0:
                pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=3)
            
            # Texte progression
            progress_text = self.small_font.render(f"{mission.progress}/{mission.target}", True, WHITE)
            self.screen.blit(progress_text, (bar_x + bar_width + 10, bar_y - 2))
            
            # Status (icône coche dessinée)
            if mission.completed and not mission.claimed:
                self._draw_check_icon(self.screen, x + 198, bar_y - 2, 12, GREEN)
                status_text = self.small_font.render("Complete!", True, GREEN)
                self.screen.blit(status_text, (x + 214, bar_y - 2))
            elif mission.claimed:
                self._draw_check_icon(self.screen, x + 198, bar_y - 2, 12, GRAY)
                status_text = self.small_font.render("Reclamee", True, GRAY)
                self.screen.blit(status_text, (x + 214, bar_y - 2))
            
            y += 72
        
        # Statistiques en bas
        y = self.menu_y + self.menu_height - 75
        pygame.draw.line(self.screen, (60, 60, 80), (x, y), (x + self.menu_width - 40, y), 1)
        y += 8
        
        stats_text = self.small_font.render(f"Missions completees: {player.missions_completed}", True, GRAY)
        self.screen.blit(stats_text, (x, y))
        
        y += 18
        sweep_cd = player.get_sweep_cooldown() if hasattr(player, 'get_sweep_cooldown') else 0
        if sweep_cd > 0:
            sweep_text = self.small_font.render(f"Balai: {int(sweep_cd)}s", True, ORANGE)
            self.screen.blit(sweep_text, (x, y))
        else:
            self._draw_check_icon(self.screen, x, y - 1, 12, GREEN)
            sweep_text = self.small_font.render("Balai: Pret!", True, GREEN)
            self.screen.blit(sweep_text, (x + 16, y))
        
    def _draw_sabotage_tab(self, game_state, start_y, height):
        """Dessine l'onglet des sabotages"""
        x = self.menu_x + 15
        y = start_y
        
        player = game_state.players[self.player_idx]
        sabotages = game_state.get_available_sabotages(self.player_idx)
        
        if not sabotages:
            no_sab = self.small_font.render("Aucun sabotage disponible", True, GRAY)
            self.screen.blit(no_sab, (x, y))
            return
            
        for i, sab in enumerate(sabotages):
            if y > self.menu_y + self.menu_height - 60:
                break
                
            # Highlight si sélectionné
            item_rect = pygame.Rect(x - 3, y - 2, self.menu_width - 30, 42)
            if i == self.selected_ingredient:
                pygame.draw.rect(self.screen, (60, 60, 80), item_rect, border_radius=5)
                pygame.draw.rect(self.screen, RED, item_rect, 2, border_radius=5)
                
            # Nom et coût
            can_afford = player.money >= sab['cost']
            name_color = WHITE if can_afford else GRAY
            name_text = self.small_font.render(sab['display_name'], True, name_color)
            self.screen.blit(name_text, (x, y))
            
            cost_color = YELLOW if can_afford else RED
            cost_text = self.small_font.render(f"${sab['cost']}", True, cost_color)
            self.screen.blit(cost_text, (x + 180, y))
            
            # Cooldown (icône coche quand prêt)
            if sab['cooldown'] > 0:
                cd_text = self.small_font.render(f"Recharge: {int(sab['cooldown'])}s", True, ORANGE)
                self.screen.blit(cd_text, (x + 10, y + 20))
            else:
                self._draw_check_icon(self.screen, x + 10, y + 19, 12, GREEN)
                ready_text = self.small_font.render("Pret!", True, GREEN)
                self.screen.blit(ready_text, (x + 26, y + 20))
                
            # Indicateur de proximité requise
            if sab['requires_proximity']:
                prox_text = self.small_font.render("Proximite requise", True, ORANGE)
                self.screen.blit(prox_text, (x + 100, y + 20))
                
            y += 48
            
    def _translate_ingredient(self, name):
        """Traduit les noms d'ingrédients en français lisible"""
        translations = {
            'galette': 'Galette',
            'viande': 'Viande',
            'sauce_fromagere': 'Sauce Fromagère',
            'frites': 'Frites',
            'sel': 'Sel',
            'pain_pita': 'Pain Pita',
            'viande_kebab': 'Viande Kebab',
            'salade': 'Salade',
            'tomates': 'Tomates',
            'oignons': 'Oignons',
            'sauce_blanche': 'Sauce Blanche',
        }
        return translations.get(name, name.replace('_', ' ').title())
