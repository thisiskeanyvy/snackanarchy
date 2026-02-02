import pygame
from config import *

class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        
    def update(self, target, zone):
        """Update camera to follow target within a zone"""
        # Calculate max scroll based on zone size
        zone_pixel_width = zone.width * TILE_SIZE
        zone_pixel_height = zone.height * TILE_SIZE
        
        # Center camera on target
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)
        
        # Limit scrolling to zone size
        x = min(0, x) # Left
        y = min(0, y) # Top
        x = max(-(zone_pixel_width - self.width), x) # Right
        y = max(-(zone_pixel_height - self.height), y) # Bottom
        
        # If zone is smaller than camera, center it
        if zone_pixel_width < self.width:
            x = (self.width - zone_pixel_width) // 2
        if zone_pixel_height < self.height:
            y = (self.height - zone_pixel_height) // 2
        
        self.camera_rect = pygame.Rect(x, y, self.width, self.height)
        self.x = -x
        self.y = -y
