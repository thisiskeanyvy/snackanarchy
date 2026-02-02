import pygame
import random
import time
from config import *
from game.dishes import create_tacos_xxl, create_kebab
from game.assets_loader import Assets

class Client(pygame.sprite.Sprite):
    def __init__(self, x, y, zone="street"):
        super().__init__()
        
        assets = Assets.get()
        self.image = assets.get_image("client")
        self.mask = assets.get_mask("client")
        
        if not self.image:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            pygame.draw.circle(self.image, self.color, (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
            self.mask = pygame.mask.from_surface(self.image)
            
        # Use actual image size for rect
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.zone = zone
        
        if zone == "tacos":
            self.dish = create_tacos_xxl()
        elif zone == "kebab":
            self.dish = create_kebab()
        else:
            self.dish = create_tacos_xxl() if random.random() < 0.5 else create_kebab()
            
        self.absurd_request = self._generate_absurd_request()
        
        self.state = "waiting"
        self.spawn_time = time.time()
        self.patience = 45
        
    def _generate_absurd_request(self):
        requests = [
            "Sans gluten mais avec double pain",
            "Cuit à la vapeur de chicha",
            "Avec supplément gras",
            "Pas trop chaud, je suis sensible",
            "Coupez le en 12 svp",
            "Avec de la mayo halal",
            "Sans oignons mais avec oignons frits",
            "Sauce algérienne-samuraï mix"
        ]
        return random.choice(requests)
        
    def update(self):
        if self.state == "waiting":
            if time.time() - self.spawn_time > self.patience:
                self.state = "angry"
                
    def draw(self, surface, camera):
        draw_x = self.rect.x - camera.x
        draw_y = self.rect.y - camera.y
        
        surface.blit(self.image, (draw_x, draw_y))
        
        # Order bubble - positioned above sprite
        font = pygame.font.SysFont(None, 24)
        order_text = font.render(self.dish.name, True, BLACK)
        bubble_rect = pygame.Rect(draw_x - 10, draw_y - 35, order_text.get_width() + 16, 28)
        pygame.draw.rect(surface, WHITE, bubble_rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, bubble_rect, 2, border_radius=8)
        surface.blit(order_text, (draw_x - 2, draw_y - 32))
        
        # Angry indicator
        if self.state == "angry":
            pygame.draw.circle(surface, (255, 0, 0), (draw_x + self.rect.width + 5, draw_y), 12)
            angry_font = pygame.font.SysFont(None, 20)
            angry_text = angry_font.render("!", True, WHITE)
            surface.blit(angry_text, (draw_x + self.rect.width + 1, draw_y - 8))
