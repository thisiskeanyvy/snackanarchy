import pygame
from config import *
from game.equipment import Fryer, Spit, Menu, Register, Toilets
from game.assets_loader import Assets

class Player(pygame.sprite.Sprite):
    def __init__(self, id, x, y, color, start_zone="street"):
        super().__init__()
        self.id = id
        self.color = color
        
        assets = Assets.get()
        sprite_name = f"player{id}"
        self.image = assets.get_image(sprite_name)
        self.mask = assets.get_mask(sprite_name)
        
        if not self.image:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            self.image.fill(color)
            self.mask = pygame.mask.from_surface(self.image)
            
        # Use actual image size for rect
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILE_SIZE, y * TILE_SIZE)
        self.speed = PLAYER_SPEED
        self.vx = 0
        self.vy = 0
        
        self.current_zone = start_zone
        
        self.money = 0
        self.reputation = 50
        
        self.equipment = {
            "fryer": Fryer(),
            "spit": Spit(),
            "menu": Menu(),
            "register": Register(),
            "toilets": Toilets()
        }
        
        self.current_client = None
        self.active_minigame = None
        self.active_sabotages = []
        
    def move(self, dx, dy):
        if self.active_minigame: return
        self.vx = dx * self.speed
        self.vy = dy * self.speed
        
    def update(self, world_map, events=None):
        if self.active_minigame:
            if events:
                self.active_minigame.update(events)
            if self.active_minigame.completed:
                pass
        else:
            new_x = self.rect.x + self.vx
            new_y = self.rect.y + self.vy
            
            zone = world_map.get_zone(self.current_zone)
            if not zone:
                return
            
            # Use center of sprite for tile collision
            center_x = new_x + self.rect.width // 2
            center_y = new_y + self.rect.height // 2
            
            tile_x = int(center_x // TILE_SIZE)
            tile_y = int(center_y // TILE_SIZE)
            
            # Check if center tile is walkable
            can_move_x = True
            can_move_y = True
            
            if self.vx != 0:
                check_x = int((new_x + self.rect.width // 2 + (self.rect.width // 3 if self.vx > 0 else -self.rect.width // 3)) // TILE_SIZE)
                if not zone.is_walkable(check_x, int((self.rect.y + self.rect.height // 2) // TILE_SIZE)):
                    can_move_x = False
                    
            if self.vy != 0:
                check_y = int((new_y + self.rect.height // 2 + (self.rect.height // 3 if self.vy > 0 else -self.rect.height // 3)) // TILE_SIZE)
                if not zone.is_walkable(int((self.rect.x + self.rect.width // 2) // TILE_SIZE), check_y):
                    can_move_y = False
            
            if can_move_x:
                self.rect.x = new_x
            if can_move_y:
                self.rect.y = new_y
                
            # Door transitions - use center
            center_tile_x = int(self.rect.centerx // TILE_SIZE)
            center_tile_y = int(self.rect.centery // TILE_SIZE)
            door = zone.get_door_at(center_tile_x, center_tile_y)
            if door:
                _, _, target_zone, target_x, target_y = door
                self.current_zone = target_zone
                self.rect.centerx = target_x * TILE_SIZE + TILE_SIZE // 2
                self.rect.centery = target_y * TILE_SIZE + TILE_SIZE // 2
        
    def draw(self, surface, camera):
        draw_x = self.rect.x - camera.x
        draw_y = self.rect.y - camera.y
        
        surface.blit(self.image, (draw_x, draw_y))
        
        if self.active_minigame:
            self.active_minigame.draw(surface, draw_x - 50, draw_y - 140)
            
    def check_collision_with(self, other):
        """Pixel-perfect collision check"""
        if not self.mask or not other.mask:
            return self.rect.colliderect(other.rect)
            
        offset_x = other.rect.x - self.rect.x
        offset_y = other.rect.y - self.rect.y
        
        overlap = self.mask.overlap(other.mask, (offset_x, offset_y))
        return overlap is not None
        
    def get_distance_to(self, other):
        return ((self.rect.centerx - other.rect.centerx)**2 + 
                (self.rect.centery - other.rect.centery)**2)**0.5
        
    def add_money(self, amount):
        self.money += amount
        
    def modify_reputation(self, amount):
        self.reputation = max(0, min(100, self.reputation + amount))
        
    def get_tile_pos(self):
        return (int(self.rect.centerx // TILE_SIZE), int(self.rect.centery // TILE_SIZE))
