"""
Menu de tutoriel - Guide les joueurs sur les règles du jeu.
Phase 1 : pancartes explicatives (pages défilantes).
Phase 2 : tutoriel interactif animé (touches à presser).
"""
import pygame
import math
import time
from config import *
from input.controls import get_key_bindings


class TutorialMenu:
    """Affiche le tutoriel du jeu avec des pages interactives"""
    
    def __init__(self, screen):
        self.screen = screen
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.visible = False
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.header_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.normal_font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        # Navigation
        self.current_page = 0
        self.start_time = time.time()
        
        # Phase : "signs" = pancartes défilantes, "interactive" = tutoriel animé
        self.phase = "signs"
        self.interactive_step = 0
        self.interactive_start_time = 0
        self._interactive_steps_cache = None  # recalculé avec les touches configurées
        
        # Colors
        self.bg_color = (25, 25, 35)
        self.panel_color = (35, 35, 50)
        self.tacos_color = (255, 140, 0)
        self.kebab_color = (76, 175, 80)
        self.highlight_color = (255, 200, 100)
        
        # Pages du tutoriel
        self.pages = self._create_tutorial_pages()
    
    def _draw_icon(self, surface, icon_type, x, y, size, color):
        """Dessine une icône personnalisée (sans emoji)"""
        cx, cy = x + size // 2, y + size // 2
        
        if icon_type == "gamepad":
            # Manette de jeu
            pygame.draw.rect(surface, color, (x + 4, y + 8, size - 8, size - 16), 2, border_radius=4)
            pygame.draw.circle(surface, color, (x + size // 3, cy), 3)
            pygame.draw.circle(surface, color, (x + 2 * size // 3, cy), 3)
        elif icon_type == "clients":
            # Silhouettes de personnes
            for i, offset in enumerate([-8, 0, 8]):
                pygame.draw.circle(surface, color, (cx + offset, y + 8), 4)
                pygame.draw.line(surface, color, (cx + offset, y + 12), (cx + offset, y + size - 8), 2)
        elif icon_type == "star":
            # Étoile
            points = []
            for i in range(5):
                angle = math.radians(-90 + i * 72)
                points.append((cx + int(size // 2.5 * math.cos(angle)), cy + int(size // 2.5 * math.sin(angle))))
                angle = math.radians(-90 + i * 72 + 36)
                points.append((cx + int(size // 5 * math.cos(angle)), cy + int(size // 5 * math.sin(angle))))
            pygame.draw.polygon(surface, color, points)
        elif icon_type == "sword":
            # Épée croisée
            pygame.draw.line(surface, color, (x + 4, y + 4), (x + size - 4, y + size - 4), 3)
            pygame.draw.line(surface, color, (x + size - 4, y + 4), (x + 4, y + size - 4), 3)
            pygame.draw.circle(surface, color, (cx, cy), 4, 2)
        elif icon_type == "checklist":
            # Liste de tâches
            pygame.draw.rect(surface, color, (x + 4, y + 4, size - 8, size - 8), 2, border_radius=3)
            for i in range(3):
                ly = y + 10 + i * 8
                pygame.draw.line(surface, color, (x + 8, ly), (x + size - 8, ly), 1)
        elif icon_type == "keyboard":
            # Clavier
            pygame.draw.rect(surface, color, (x + 2, y + 8, size - 4, size - 16), 2, border_radius=3)
            for i in range(3):
                for j in range(4):
                    kx = x + 6 + j * 6
                    ky = y + 12 + i * 5
                    pygame.draw.rect(surface, color, (kx, ky, 4, 3), 0)
        elif icon_type == "lightbulb":
            # Ampoule
            pygame.draw.circle(surface, color, (cx, y + size // 3), size // 4, 2)
            pygame.draw.rect(surface, color, (cx - 4, y + size // 2, 8, 6), 0)
            pygame.draw.line(surface, color, (cx - 4, y + size // 2 + 8), (cx + 4, y + size // 2 + 8), 2)
    
    def _create_tutorial_pages(self):
        """Crée les pages du tutoriel"""
        return [
            {
                'title': "Bienvenue dans Snack Anarchy!",
                'icon': "gamepad",
                'sections': [
                    {
                        'header': "Le Concept",
                        'content': [
                            "Deux restaurants rivaux s'affrontent dans une bataille",
                            "epique pour devenir le meilleur snack de la ville!",
                            "",
                            "Joueur 1 gere le restaurant TACOS (orange)",
                            "Joueur 2 gere le restaurant KEBAB (vert)"
                        ]
                    },
                    {
                        'header': "Objectif",
                        'content': [
                            "Gagner le plus d'argent possible avant la fin du temps!",
                            "Servez des clients, gerez votre reputation,",
                            "et n'hesitez pas a saboter votre adversaire!"
                        ]
                    }
                ]
            },
            {
                'title': "Servir les Clients",
                'icon': "clients",
                'sections': [
                    {
                        'header': "Comment servir?",
                        'content': [
                            "1. Les clients entrent dans votre restaurant",
                            "2. Approchez-vous d'un client en file d'attente",
                            "3. Appuyez sur la touche d'INTERACTION",
                            "4. Reussissez le mini-jeu pour servir le client!",
                            "",
                            "Chaque client servi rapporte 20 euros et +2% reputation"
                        ]
                    },
                    {
                        'header': "Gestion du Stock",
                        'content': [
                            "Surveillez vos ingredients! Sans stock, pas de service.",
                            "Reapprovisionnez-vous regulierement via l'inventaire."
                        ]
                    }
                ]
            },
            {
                'title': "La Reputation",
                'icon': "star",
                'sections': [
                    {
                        'header': "Pourquoi c'est important?",
                        'content': [
                            "Votre reputation attire plus ou moins de clients!",
                            "Plus elle est haute, plus vous aurez de clients.",
                            "",
                            "Reputation initiale: 50%"
                        ]
                    },
                    {
                        'header': "Gains et Pertes",
                        'content': [
                            "+ Servir un client: +2% reputation",
                            "- Client qui part impatient: -1% reputation",
                            "- Tuer un client dans son resto: -5% reputation",
                            "",
                            "Attention! Une mauvaise reputation = moins de clients!"
                        ]
                    }
                ]
            },
            {
                'title': "Combat et Sabotage",
                'icon': "sword",
                'sections': [
                    {
                        'header': "Les Armes",
                        'content': [
                            "Des armes apparaissent aleatoirement sur la carte!",
                            "Ramassez-les pour pouvoir attaquer.",
                            "",
                            "Types d'armes: Couteau, Poele, Extincteur..."
                        ]
                    },
                    {
                        'header': "Strategie de Sabotage",
                        'content': [
                            "Tuez des clients dans le restaurant ADVERSE!",
                            "Cela fait baisser la reputation de votre rival.",
                            "",
                            "Astuce: Infiltrez-vous discretement chez l'ennemi!"
                        ]
                    }
                ]
            },
            {
                'title': "Missions",
                'icon': "checklist",
                'sections': [
                    {
                        'header': "Accomplir des Missions",
                        'content': [
                            "Chaque partie vous propose 3 missions actives.",
                            "Accomplissez-les pour gagner des recompenses!",
                            "",
                            "Exemples: Servir X tacos, Gagner X euros, etc."
                        ]
                    },
                    {
                        'header': "Recompenses",
                        'content': [
                            "Chaque mission completee donne:",
                            "- De l'argent bonus",
                            "- Des points de reputation",
                            "",
                            "Les recompenses sont automatiques!"
                        ]
                    }
                ]
            },
            {
                'title': "Controles",
                'icon': "keyboard",
                'sections': [
                    {
                        'header': "Joueur 1 (Tacos)",
                        'content': [
                            "Deplacement: ZQSD",
                            "Interaction: E",
                            "Attaque: R",
                            "Inventaire: TAB"
                        ]
                    },
                    {
                        'header': "Joueur 2 (Kebab)",
                        'content': [
                            "Deplacement: Fleches directionnelles",
                            "Interaction: ESPACE",
                            "Attaque: CTRL droit",
                            "Inventaire: ENTREE"
                        ]
                    }
                ]
            },
            {
                'title': "Conseils de Pro",
                'icon': "lightbulb",
                'sections': [
                    {
                        'header': "Strategies Gagnantes",
                        'content': [
                            "1. Servez rapidement pour ne pas perdre de clients",
                            "2. Gardez toujours un oeil sur votre stock",
                            "3. Accomplissez les missions pour des bonus",
                            "4. Sabotez au bon moment, pas trop tot!"
                        ]
                    },
                    {
                        'header': "A Eviter",
                        'content': [
                            "- Ne tuez pas de clients dans VOTRE restaurant",
                            "- Ne laissez pas les clients attendre trop longtemps",
                            "- N'ignorez pas les missions, elles rapportent gros!"
                        ]
                    }
                ]
            }
        ]
    
    def _get_interactive_steps(self):
        """Construit les étapes du tutoriel interactif (touches à presser)."""
        if self._interactive_steps_cache is not None:
            return self._interactive_steps_cache
        kb = get_key_bindings()
        p1, p2 = 'player1', 'player2'
        steps = [
            {
                'instruction': "Déplace-toi avec tes touches de déplacement !",
                'keys': [
                    kb.get_key(p1, 'up'), kb.get_key(p1, 'down'), kb.get_key(p1, 'left'), kb.get_key(p1, 'right'),
                    kb.get_key(p2, 'up'), kb.get_key(p2, 'down'), kb.get_key(p2, 'left'), kb.get_key(p2, 'right'),
                ],
                'key_labels': f"{kb.get_key_name(kb.get_key(p1, 'up'))}{kb.get_key_name(kb.get_key(p1, 'left'))}{kb.get_key_name(kb.get_key(p1, 'down'))}{kb.get_key_name(kb.get_key(p1, 'right'))} / Flèches",
            },
            {
                'instruction': "Appuie sur ta touche d'interaction (servir un client)",
                'keys': [kb.get_key(p1, 'interact'), kb.get_key(p2, 'interact')],
                'key_labels': f"J1: {kb.get_key_name(kb.get_key(p1, 'interact'))}  |  J2: {kb.get_key_name(kb.get_key(p2, 'interact'))}",
            },
            {
                'instruction': "Ouvre ton inventaire",
                'keys': [kb.get_key(p1, 'inventory'), kb.get_key(p2, 'inventory')],
                'key_labels': f"J1: {kb.get_key_name(kb.get_key(p1, 'inventory'))}  |  J2: {kb.get_key_name(kb.get_key(p2, 'inventory'))}",
            },
            {
                'instruction': "Ouvre ta carte des plats",
                'keys': [kb.get_key(p1, 'carte'), kb.get_key(p2, 'carte')],
                'key_labels': f"J1: {kb.get_key_name(kb.get_key(p1, 'carte'))}  |  J2: {kb.get_key_name(kb.get_key(p2, 'carte'))}",
            },
            {
                'instruction': "Bravo ! Appuie pour terminer le tutoriel",
                'keys': [pygame.K_SPACE, pygame.K_RETURN],
                'key_labels': "ESPACE ou ENTRÉE",
            },
        ]
        self._interactive_steps_cache = steps
        return steps
    
    def _reset_interactive_cache(self):
        """Invalide le cache des étapes (si les touches sont reconfigurées)."""
        self._interactive_steps_cache = None
    
    def toggle(self):
        """Ouvre/ferme le tutoriel"""
        self.visible = not self.visible
        if self.visible:
            self.current_page = 0
            self.phase = "signs"
            self.interactive_step = 0
            self.start_time = time.time()
            self._reset_interactive_cache()
    
    def close(self):
        """Ferme le tutoriel"""
        self.visible = False
        self.phase = "signs"
    
    def _start_interactive_phase(self):
        """Passe à la phase tutoriel interactif après les pancartes."""
        self.phase = "interactive"
        self.interactive_step = 0
        self.interactive_start_time = time.time()
    
    def handle_input(self, event):
        """Gère les entrées utilisateur"""
        if not self.visible:
            return None
        
        if self.phase == "interactive":
            return self._handle_interactive_input(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return "close"
            
            # Navigation
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self.current_page > 0:
                    self.current_page -= 1
                    self.start_time = time.time()
                return "navigate"
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_SPACE, pygame.K_RETURN):
                if self.current_page < len(self.pages) - 1:
                    self.current_page += 1
                    self.start_time = time.time()
                else:
                    self._start_interactive_phase()
                    return "navigate"
                return "navigate"
        
        # Support souris
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_mouse_click(event.pos)
        
        return None
    
    def _handle_interactive_input(self, event):
        """Gère les entrées pendant la phase tutoriel interactif."""
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_ESCAPE:
            self.close()
            return "close"
        steps = self._get_interactive_steps()
        if self.interactive_step >= len(steps):
            return None
        if event.key in steps[self.interactive_step]['keys']:
            self.interactive_step += 1
            self.interactive_start_time = time.time()
            if self.interactive_step >= len(steps):
                self.close()
                return "close"
            return "navigate"
        return None
    
    def _handle_mouse_click(self, pos):
        """Gère les clics souris"""
        # Bouton fermer
        close_rect = pygame.Rect(self.width - 60, 20, 40, 40)
        if close_rect.collidepoint(pos):
            self.close()
            return "close"
        
        # Boutons de navigation
        nav_y = self.height - 70
        prev_rect = pygame.Rect(self.width // 2 - 180, nav_y, 140, 40)
        next_rect = pygame.Rect(self.width // 2 + 40, nav_y, 140, 40)
        
        if prev_rect.collidepoint(pos) and self.current_page > 0:
            self.current_page -= 1
            self.start_time = time.time()
            return "navigate"
        
        if next_rect.collidepoint(pos):
            if self.current_page < len(self.pages) - 1:
                self.current_page += 1
                self.start_time = time.time()
            else:
                self._start_interactive_phase()
                return "navigate"
            return "navigate"
        
        return None
    
    def draw(self):
        """Dessine le menu de tutoriel (pancartes ou phase interactif)."""
        if not self.visible:
            return
        if self.phase == "interactive":
            self._draw_interactive_phase()
            return
        self._draw_signs_phase()
    
    def _draw_signs_phase(self):
        """Dessine la phase pancartes (pages défilantes)."""
        elapsed = time.time() - self.start_time
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        self.screen.blit(overlay, (0, 0))
        page = self.pages[self.current_page]
        
        # Titre avec icône
        title_y = 45 + math.sin(elapsed * 2) * 2
        
        # Icône à gauche du titre
        icon_size = 36
        title_surface = self.title_font.render(page['title'], True, self.tacos_color)
        total_width = icon_size + 15 + title_surface.get_width()
        icon_x = (self.width - total_width) // 2
        
        self._draw_icon(self.screen, page['icon'], icon_x, int(title_y) - 5, icon_size, self.tacos_color)
        self.screen.blit(title_surface, (icon_x + icon_size + 15, title_y))
        
        # Bouton fermer
        self._draw_close_button()
        
        # Contenu
        content_rect = pygame.Rect(60, 100, self.width - 120, self.height - 200)
        pygame.draw.rect(self.screen, self.panel_color, content_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.tacos_color, content_rect, 2, border_radius=12)
        
        # Sections côte à côte
        section_width = (content_rect.width - 40) // 2
        
        for i, section in enumerate(page['sections']):
            x = content_rect.x + 20 + (i % 2) * (section_width + 20)
            y = content_rect.y + 25
            
            if i >= 2:
                y += 180
            
            # En-tête de section avec ligne
            header = self.header_font.render(section['header'], True, self.highlight_color)
            self.screen.blit(header, (x, y))
            
            pygame.draw.line(self.screen, self.tacos_color,
                            (x, y + 32), (x + section_width - 10, y + 32), 2)
            
            # Contenu
            line_y = y + 45
            for line in section['content']:
                if line == "":
                    line_y += 8
                    continue
                
                text = self.normal_font.render(line, True, (200, 200, 200))
                self.screen.blit(text, (x, line_y))
                line_y += 26
        
        # Navigation
        self._draw_navigation()
        
        # Indicateur de page
        self._draw_page_indicator()
    
    def _draw_interactive_phase(self):
        """Dessine le tutoriel interactif animé (après les pancartes)."""
        elapsed = time.time() - self.interactive_start_time
        steps = self._get_interactive_steps()
        if self.interactive_step >= len(steps):
            return
        step = steps[self.interactive_step]
        
        # Overlay avec léger dégradé
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Titre animé (ondulation)
        title_y = 50 + math.sin(elapsed * 2.5) * 4
        title = self.title_font.render("Tutoriel interactif", True, self.highlight_color)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, int(title_y))))
        
        # Sous-titre
        sub = self.small_font.render("Appuie sur la touche indiquée pour continuer", True, (140, 140, 160))
        self.screen.blit(sub, sub.get_rect(center=(self.width // 2, int(title_y) + 44)))
        
        # Panneau central avec instruction
        panel_w, panel_h = 700, 220
        panel = pygame.Rect((self.width - panel_w) // 2, (self.height - panel_h) // 2 - 20, panel_w, panel_h)
        # Bordure animée (pulse)
        pulse = 0.7 + 0.3 * math.sin(elapsed * 3)
        r, g, b = self.tacos_color
        border_color = (min(255, int(r * pulse)), min(255, int(200 * pulse)), min(255, int(100 * pulse)))
        pygame.draw.rect(self.screen, self.panel_color, panel, border_radius=16)
        pygame.draw.rect(self.screen, border_color, panel, 3, border_radius=16)
        
        # Instruction
        inst_surf = self.header_font.render(step['instruction'], True, WHITE)
        self.screen.blit(inst_surf, inst_surf.get_rect(center=(self.width // 2, panel.centery - 45)))
        
        # Touche(s) à presser : boîte animée (lueur pulsée)
        key_label = step['key_labels']
        key_font = pygame.font.SysFont("Arial", 28, bold=True)
        key_surf = key_font.render(key_label, True, WHITE)
        box_w = key_surf.get_width() + 48
        box_h = 52
        box_rect = pygame.Rect((self.width - box_w) // 2, panel.centery + 15, box_w, box_h)
        glow = max(0, int(30 * (0.5 + 0.5 * math.sin(elapsed * 3))))
        pygame.draw.rect(self.screen, (40 + glow, 30 + glow // 2, 20), box_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.tacos_color, box_rect, 2, border_radius=12)
        # Redimensionner légèrement le texte pour l'effet pulse (optionnel: on garde le texte normal)
        self.screen.blit(key_surf, key_surf.get_rect(center=box_rect.center))
        
        # Indicateur d'étape
        step_y = self.height - 55
        step_text = self.small_font.render(
            f"Étape {self.interactive_step + 1} / {len(steps)}",
            True, (120, 120, 140)
        )
        self.screen.blit(step_text, step_text.get_rect(center=(self.width // 2, step_y)))
        # Barre de progression
        bar_w, bar_h = 200, 6
        bar_rect = pygame.Rect((self.width - bar_w) // 2, step_y + 18, bar_w, bar_h)
        pygame.draw.rect(self.screen, (50, 50, 60), bar_rect, border_radius=3)
        fill_w = int(bar_w * (self.interactive_step + 1) / len(steps))
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_h)
            pygame.draw.rect(self.screen, self.kebab_color, fill_rect, border_radius=3)
        
        # ÉCHAP pour quitter
        esc_text = self.small_font.render("ÉCHAP pour quitter", True, (80, 80, 100))
        self.screen.blit(esc_text, (self.width - esc_text.get_width() - 24, self.height - 28))
    
    def _draw_close_button(self):
        """Dessine le bouton fermer"""
        close_rect = pygame.Rect(self.width - 60, 20, 40, 40)
        pygame.draw.rect(self.screen, (80, 40, 40), close_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 80, 80), close_rect, 2, border_radius=8)
        
        # X dessiné
        cx, cy = close_rect.center
        pygame.draw.line(self.screen, WHITE, (cx - 8, cy - 8), (cx + 8, cy + 8), 3)
        pygame.draw.line(self.screen, WHITE, (cx + 8, cy - 8), (cx - 8, cy + 8), 3)
    
    def _draw_navigation(self):
        """Dessine les boutons de navigation"""
        nav_y = self.height - 70
        
        # Bouton Précédent
        if self.current_page > 0:
            prev_rect = pygame.Rect(self.width // 2 - 180, nav_y, 140, 40)
            pygame.draw.rect(self.screen, self.panel_color, prev_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.tacos_color, prev_rect, 2, border_radius=8)
            
            # Flèche gauche
            arrow_x = prev_rect.x + 15
            arrow_y = prev_rect.centery
            pygame.draw.polygon(self.screen, WHITE, [
                (arrow_x + 8, arrow_y - 6),
                (arrow_x, arrow_y),
                (arrow_x + 8, arrow_y + 6)
            ])
            
            prev_text = self.normal_font.render("Precedent", True, WHITE)
            self.screen.blit(prev_text, (prev_rect.x + 35, prev_rect.centery - prev_text.get_height() // 2))
        
        # Bouton Suivant / Terminer
        next_rect = pygame.Rect(self.width // 2 + 40, nav_y, 140, 40)
        
        if self.current_page < len(self.pages) - 1:
            pygame.draw.rect(self.screen, self.tacos_color, next_rect, border_radius=8)
            next_text = self.normal_font.render("Suivant", True, BLACK)
            self.screen.blit(next_text, (next_rect.x + 25, next_rect.centery - next_text.get_height() // 2))
            
            # Flèche droite
            arrow_x = next_rect.right - 25
            arrow_y = next_rect.centery
            pygame.draw.polygon(self.screen, BLACK, [
                (arrow_x - 8, arrow_y - 6),
                (arrow_x, arrow_y),
                (arrow_x - 8, arrow_y + 6)
            ])
        else:
            pygame.draw.rect(self.screen, self.kebab_color, next_rect, border_radius=8)
            next_text = self.normal_font.render("Terminer", True, BLACK)
            self.screen.blit(next_text, (next_rect.x + 25, next_rect.centery - next_text.get_height() // 2))
            
            # Checkmark
            check_x = next_rect.right - 25
            check_y = next_rect.centery
            pygame.draw.lines(self.screen, BLACK, False, [
                (check_x - 6, check_y),
                (check_x - 2, check_y + 4),
                (check_x + 6, check_y - 6)
            ], 3)
    
    def _draw_page_indicator(self):
        """Dessine l'indicateur de progression"""
        indicator_y = self.height - 25
        dot_size = 8
        dot_spacing = 18
        total_width = len(self.pages) * dot_spacing
        start_x = (self.width - total_width) // 2
        
        for i in range(len(self.pages)):
            x = start_x + i * dot_spacing + dot_size // 2
            color = self.tacos_color if i == self.current_page else (80, 80, 100)
            pygame.draw.circle(self.screen, color, (x, indicator_y), dot_size // 2)
        
        # Texte de page
        page_text = self.small_font.render(
            f"Page {self.current_page + 1} / {len(self.pages)}", 
            True, (100, 100, 120)
        )
        self.screen.blit(page_text, page_text.get_rect(center=(self.width // 2, indicator_y - 18)))
