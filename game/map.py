import pygame
from config import *
from game.assets_loader import Assets

class Zone:
    """Represents a single zone (room) in the game"""
    def __init__(self, name, width, height, bg_image_name=None):
        self.name = name
        self.width = width
        self.height = height
        self.bg_image_name = bg_image_name
        self.tiles = [[TILE_FLOOR for _ in range(width)] for _ in range(height)]
        self.doors = []
        self.walkable_area = []
        
    def set_tile(self, x, y, tile_type):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type
            
    def add_door(self, x, y, target_zone, target_x, target_y):
        self.tiles[y][x] = TILE_DOOR
        self.doors.append((x, y, target_zone, target_x, target_y))
        
    def set_walkable_rect(self, x, y, w, h):
        self.walkable_area.append(pygame.Rect(x, y, w, h))
        
    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        if self.walkable_area:
            for rect in self.walkable_area:
                if rect.collidepoint(x, y):
                    return True
            for door in self.doors:
                if door[0] == x and door[1] == y:
                    return True
            return False
            
        tile = self.tiles[y][x]
        return tile in [TILE_FLOOR, TILE_DOOR, TILE_STREET, TILE_SIDEWALK]
        
    def get_door_at(self, x, y):
        for door in self.doors:
            if door[0] == x and door[1] == y:
                return door
        return None

class TacosRestaurant(Zone):
    def __init__(self):
        super().__init__("tacos", RESTAURANT_WIDTH, RESTAURANT_HEIGHT, "interior_tacos")
        self._setup()
        
    def _setup(self):
        # Walkable area - main floor area
        self.set_walkable_rect(1, 3, self.width - 2, self.height - 4)
        
        # Door at bottom center
        door_x = self.width // 2
        # Exit leads to sidewalk in front of tacos facade (tile 2, row 3)
        self.add_door(door_x, self.height - 1, "street", 2, 4)

class KebabRestaurant(Zone):
    def __init__(self):
        super().__init__("kebab", RESTAURANT_WIDTH, RESTAURANT_HEIGHT, "interior_kebab")
        self._setup()
        
    def _setup(self):
        # Walkable area
        self.set_walkable_rect(1, 3, self.width - 2, self.height - 4)
        
        # Door at bottom center
        door_x = self.width // 2
        # Exit leads to sidewalk in front of kebab facade (tile 9, row 3)
        self.add_door(door_x, self.height - 1, "street", 9, 4)

class Street(Zone):
    def __init__(self):
        # Compact street: 14 tiles wide, 8 tall
        super().__init__("street", 14, 8, None)
        self._setup()
        
    def _setup(self):
        # Building facades (rows 0-2) - not walkable
        for y in range(3):
            for x in range(self.width):
                self.set_tile(x, y, TILE_WALL)
                
        # Sidewalk (rows 3-4)
        for y in range(3, 5):
            for x in range(self.width):
                self.set_tile(x, y, TILE_SIDEWALK)
                
        # Road (rows 5-7)
        for y in range(5, self.height):
            for x in range(self.width):
                self.set_tile(x, y, TILE_STREET)
        
        # Doors aligned with facade entrances
        # Tacos door at tile 2 (under tacos facade entrance)
        self.add_door(2, 3, "tacos", 5, 6)
        # Kebab door at tile 9 (under kebab facade entrance)
        self.add_door(9, 3, "kebab", 5, 6)

class WorldMap:
    """Manages all zones and transitions"""
    def __init__(self):
        self.zones = {
            "tacos": TacosRestaurant(),
            "kebab": KebabRestaurant(),
            "street": Street()
        }
        
    def get_zone(self, name):
        return self.zones.get(name)
        
    def draw_zone(self, zone, surface, camera):
        assets = Assets.get()
        
        # For restaurants: draw full background image
        if zone.bg_image_name:
            bg = assets.get_image(zone.bg_image_name)
            if bg:
                pos = (-camera.x, -camera.y)
                surface.blit(bg, pos)
                
                # Draw exit door indicator
                door_img = assets.get_image("door")
                for door in zone.doors:
                    dx, dy = door[0], door[1]
                    door_pos = (dx * TILE_SIZE - camera.x, dy * TILE_SIZE - camera.y)
                    if door_img:
                        surface.blit(door_img, door_pos)
                return
        
        # For street
        sidewalk_img = assets.get_image("sidewalk")
        road_img = assets.get_image("road")
        facade_tacos = assets.get_image("facade_tacos")
        facade_kebab = assets.get_image("facade_kebab")
        door_img = assets.get_image("door")
        
        # Draw base tiles first
        for y in range(zone.height):
            for x in range(zone.width):
                tile = zone.tiles[y][x]
                pos = (x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y)
                
                if tile == TILE_SIDEWALK and sidewalk_img:
                    surface.blit(sidewalk_img, pos)
                elif tile == TILE_STREET and road_img:
                    surface.blit(road_img, pos)
                elif tile == TILE_WALL:
                    # Dark background for buildings
                    pygame.draw.rect(surface, (40, 35, 50), (pos[0], pos[1], TILE_SIZE, TILE_SIZE))
                elif tile == TILE_DOOR:
                    # Sidewalk under door
                    if sidewalk_img:
                        surface.blit(sidewalk_img, pos)
                    
        # Draw facades over building area
        # Tacos facade: tiles 0-5, rows 0-2 (6 tiles wide, 3 tiles tall)
        if facade_tacos:
            facade_pos = (0 - camera.x, 0 - camera.y)
            surface.blit(facade_tacos, facade_pos)
            
        # Kebab facade: tiles 7-12, rows 0-2
        if facade_kebab:
            facade_pos = (7 * TILE_SIZE - camera.x, 0 - camera.y)
            surface.blit(facade_kebab, facade_pos)
            
        # Draw door markers on sidewalk
        for door in zone.doors:
            dx, dy = door[0], door[1]
            door_pos = (dx * TILE_SIZE - camera.x, dy * TILE_SIZE - camera.y)
            if door_img:
                surface.blit(door_img, door_pos)

class Map:
    def __init__(self):
        self.world = WorldMap()
        self.width = 14
        self.height = 8
        self.tile_size = TILE_SIZE
        
    def draw(self, surface, camera, zone_name="street"):
        zone = self.world.get_zone(zone_name)
        if zone:
            self.world.draw_zone(zone, surface, camera)
