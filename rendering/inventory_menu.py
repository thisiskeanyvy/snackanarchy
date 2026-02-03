"""
Menu d'inventaire pour afficher le stock de nourriture et les équipements
"""
import pygame
from config import *

class InventoryMenu:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.active_player = 0  # 0 ou 1
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 42)
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)
        
        # Position du menu
        self.menu_width = 400
        self.menu_height = 500
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        
        # Tab sélectionné
        self.current_tab = 0  # 0 = Stock, 1 = Équipement, 2 = Sabotages
        self.tabs = ["Stock", "Équipement", "Sabotages"]
        
        # Scroll
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Sélection pour réappro
        self.selected_ingredient = 0
        
    def toggle(self, player_idx):
        """Ouvre/ferme l'inventaire pour un joueur"""
        if self.visible and self.active_player == player_idx:
            self.visible = False
        else:
            self.visible = True
            self.active_player = player_idx
            self.scroll_offset = 0
            self.selected_ingredient = 0
            
    def close(self):
        self.visible = False
        
    def handle_input(self, event, game_state):
        """Gère les inputs dans le menu d'inventaire"""
        if not self.visible:
            return None
            
        if event.type == pygame.KEYDOWN:
            # Fermer le menu
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i or event.key == pygame.K_TAB:
                self.close()
                return "close"
                
            # Navigation tabs
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.current_tab = (self.current_tab - 1) % len(self.tabs)
                self.scroll_offset = 0
                self.selected_ingredient = 0
                return "navigate"
                
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.current_tab = (self.current_tab + 1) % len(self.tabs)
                self.scroll_offset = 0
                self.selected_ingredient = 0
                return "navigate"
                
            # Navigation verticale dans le stock
            if self.current_tab == 0:
                player = game_state.players[self.active_player]
                ingredients = list(player.food_stock.ingredients.keys())
                
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_ingredient = max(0, self.selected_ingredient - 1)
                    return "navigate"
                    
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_ingredient = min(len(ingredients) - 1, self.selected_ingredient + 1)
                    return "navigate"
                    
                # Réapprovisionner l'ingrédient sélectionné
                if event.key == pygame.K_RETURN or event.key == pygame.K_e:
                    if ingredients:
                        ing_name = ingredients[self.selected_ingredient]
                        amount, cost = player.restock(ing_name)
                        if amount > 0:
                            return f"restock_{ing_name}"
                    return None
                    
            # Sabotages
            if self.current_tab == 2:
                sabotages = game_state.get_available_sabotages(self.active_player)
                
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_ingredient = max(0, self.selected_ingredient - 1)
                    return "navigate"
                    
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_ingredient = min(len(sabotages) - 1, self.selected_ingredient + 1)
                    return "navigate"
                    
                # Exécuter le sabotage sélectionné
                if event.key == pygame.K_RETURN or event.key == pygame.K_e:
                    if sabotages and self.selected_ingredient < len(sabotages):
                        sabotage = sabotages[self.selected_ingredient]
                        if sabotage['cooldown'] <= 0:
                            success, msg = game_state.handle_sabotage(self.active_player, sabotage['name'])
                            if success:
                                self.close()
                                return f"sabotage_{sabotage['name']}"
                    return None
                    
        return None
        
    def draw(self, game_state):
        """Dessine le menu d'inventaire"""
        if not self.visible:
            return
            
        player = game_state.players[self.active_player]
        
        # Overlay semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Fond du menu
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(self.screen, (30, 30, 40), menu_rect, border_radius=15)
        pygame.draw.rect(self.screen, MENU_ACCENT, menu_rect, 3, border_radius=15)
        
        # Titre
        title_color = ORANGE if self.active_player == 0 else GREEN
        title = self.title_font.render(f"Inventaire - {player.username}", True, title_color)
        self.screen.blit(title, (self.menu_x + 20, self.menu_y + 15))
        
        # Argent disponible
        money_text = self.font.render(f"💰 ${player.money}", True, YELLOW)
        self.screen.blit(money_text, (self.menu_x + self.menu_width - 120, self.menu_y + 20))
        
        # Tabs
        tab_y = self.menu_y + 60
        tab_width = (self.menu_width - 40) // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_x = self.menu_x + 20 + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width - 5, 35)
            
            if i == self.current_tab:
                pygame.draw.rect(self.screen, MENU_ACCENT, tab_rect, border_radius=5)
                text_color = BLACK
            else:
                pygame.draw.rect(self.screen, (50, 50, 60), tab_rect, border_radius=5)
                pygame.draw.rect(self.screen, (80, 80, 90), tab_rect, 1, border_radius=5)
                text_color = WHITE
                
            tab_text = self.font.render(tab, True, text_color)
            text_x = tab_x + (tab_width - 5 - tab_text.get_width()) // 2
            self.screen.blit(tab_text, (text_x, tab_y + 7))
            
        # Contenu selon le tab
        content_y = tab_y + 50
        content_height = self.menu_height - 140
        
        if self.current_tab == 0:
            self._draw_stock_tab(player, content_y, content_height)
        elif self.current_tab == 1:
            self._draw_equipment_tab(player, content_y, content_height)
        else:
            self._draw_sabotage_tab(game_state, content_y, content_height)
            
        # Instructions en bas
        instructions = "↑↓ Naviguer | ← → Tabs | Entrée: Sélectionner | Échap: Fermer"
        inst_text = self.small_font.render(instructions, True, GRAY)
        self.screen.blit(inst_text, (self.menu_x + 20, self.menu_y + self.menu_height - 30))
        
    def _draw_stock_tab(self, player, start_y, height):
        """Dessine l'onglet du stock"""
        x = self.menu_x + 20
        y = start_y
        
        ingredients = list(player.food_stock.ingredients.items())
        
        for i, (name, data) in enumerate(ingredients):
            if y > self.menu_y + self.menu_height - 60:
                break
                
            # Highlight si sélectionné
            item_rect = pygame.Rect(x - 5, y - 2, self.menu_width - 40, 35)
            if i == self.selected_ingredient:
                pygame.draw.rect(self.screen, (60, 60, 80), item_rect, border_radius=5)
                pygame.draw.rect(self.screen, MENU_ACCENT, item_rect, 2, border_radius=5)
                
            # Nom de l'ingrédient (traduit)
            display_name = self._translate_ingredient(name)
            name_text = self.font.render(display_name, True, WHITE)
            self.screen.blit(name_text, (x, y))
            
            # Barre de stock
            bar_x = x + 160
            bar_width = 120
            bar_height = 18
            
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
            self.screen.blit(qty_text, (bar_x + bar_width + 10, y + 5))
            
            # Prix réappro si sélectionné
            if i == self.selected_ingredient:
                needed = data['max'] - data['quantity']
                cost = int(needed * data['price'])
                if needed > 0:
                    restock_text = self.small_font.render(f"Réappro: ${cost}", True, YELLOW)
                    self.screen.blit(restock_text, (x, y + 22))
                    
            y += 40
            
        # Status broche
        y += 10
        if player.food_stock.is_spit_available():
            spit_text = self.font.render("🍖 Broche: OK", True, GREEN)
        else:
            cooldown = int(player.food_stock.get_spit_cooldown())
            spit_text = self.font.render(f"🍖 Broche volée! ({cooldown}s)", True, RED)
        self.screen.blit(spit_text, (x, y))
        
    def _draw_equipment_tab(self, player, start_y, height):
        """Dessine l'onglet des équipements"""
        x = self.menu_x + 20
        y = start_y
        
        equipment_icons = {
            'fryer': '🍟',
            'spit': '🍖',
            'menu': '📋',
            'register': '💰',
            'toilets': '🚽'
        }
        
        equipment_names = {
            'fryer': 'Friteuse',
            'spit': 'Broche',
            'menu': 'Menu',
            'register': 'Caisse',
            'toilets': 'Toilettes'
        }
        
        for eq_key, eq in player.equipment.items():
            icon = equipment_icons.get(eq_key, '⚙️')
            name = equipment_names.get(eq_key, eq_key)
            status = eq.get_status()
            
            # Couleur selon status
            if status == "OK":
                status_color = GREEN
            else:
                status_color = RED
                
            # Ligne équipement
            eq_text = self.font.render(f"{icon} {name}", True, WHITE)
            self.screen.blit(eq_text, (x, y))
            
            status_text = self.font.render(status, True, status_color)
            self.screen.blit(status_text, (x + 200, y))
            
            # Description
            desc_text = self.small_font.render(eq.description, True, GRAY)
            self.screen.blit(desc_text, (x + 20, y + 25))
            
            y += 55
            
        # Arme équipée
        y += 10
        weapon_info = player.get_weapon_info()
        if weapon_info:
            weapon_text = self.font.render(f"🔪 Arme: {weapon_info['name']} ({weapon_info['uses']} coups)", True, RED)
        else:
            weapon_text = self.font.render("🔪 Arme: Aucune", True, GRAY)
        self.screen.blit(weapon_text, (x, y))
        
    def _draw_sabotage_tab(self, game_state, start_y, height):
        """Dessine l'onglet des sabotages"""
        x = self.menu_x + 20
        y = start_y
        
        player = game_state.players[self.active_player]
        sabotages = game_state.get_available_sabotages(self.active_player)
        
        if not sabotages:
            no_sab = self.font.render("Aucun sabotage disponible", True, GRAY)
            self.screen.blit(no_sab, (x, y))
            return
            
        for i, sab in enumerate(sabotages):
            if y > self.menu_y + self.menu_height - 80:
                break
                
            # Highlight si sélectionné
            item_rect = pygame.Rect(x - 5, y - 2, self.menu_width - 40, 50)
            if i == self.selected_ingredient:
                pygame.draw.rect(self.screen, (60, 60, 80), item_rect, border_radius=5)
                pygame.draw.rect(self.screen, RED, item_rect, 2, border_radius=5)
                
            # Nom et coût
            can_afford = player.money >= sab['cost']
            name_color = WHITE if can_afford else GRAY
            name_text = self.font.render(sab['display_name'], True, name_color)
            self.screen.blit(name_text, (x, y))
            
            cost_color = YELLOW if can_afford else RED
            cost_text = self.font.render(f"${sab['cost']}", True, cost_color)
            self.screen.blit(cost_text, (x + 200, y))
            
            # Cooldown
            if sab['cooldown'] > 0:
                cd_text = self.small_font.render(f"Recharge: {int(sab['cooldown'])}s", True, ORANGE)
                self.screen.blit(cd_text, (x + 20, y + 25))
            else:
                ready_text = self.small_font.render("Prêt!", True, GREEN)
                self.screen.blit(ready_text, (x + 20, y + 25))
                
            # Indicateur de proximité requise
            if sab['requires_proximity']:
                prox_text = self.small_font.render("⚠ Nécessite proximité", True, ORANGE)
                self.screen.blit(prox_text, (x + 120, y + 25))
                
            y += 55
            
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
