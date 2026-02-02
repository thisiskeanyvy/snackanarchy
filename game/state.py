import pygame
import random
import time
from game.map import WorldMap
from game.player import Player
from game.client import Client
from game.minigames import MiniGame
from game.events import EventManager
from config import *

class GameState:
    def __init__(self):
        self.world_map = WorldMap()
        
        self.players = [
            Player(1, 5, 5, PLAYER_1_COLOR, "tacos"),
            Player(2, 5, 5, PLAYER_2_COLOR, "kebab")
        ]
        
        self.clients = []
        self.last_spawn_time = time.time()
        self.spawn_interval = 8.0
        
        self.event_manager = EventManager(self)
        
        self.start_time = time.time()
        self.game_duration = DEFAULT_DURATION
        self.game_over = False
        
    def update(self, events, input_action):
        if self.game_over:
            return
            
        elapsed = time.time() - self.start_time
        if elapsed >= self.game_duration:
            self.game_over = True
            return
        
        for player in self.players:
            player.update(self.world_map, events)
            
            if player.active_minigame and player.active_minigame.completed:
                if player.active_minigame.success:
                    player.add_money(20)
                    player.modify_reputation(5)
                else:
                    player.modify_reputation(-5)
                
                player.active_minigame = None
                if player.current_client in self.clients:
                    self.clients.remove(player.current_client)
                player.current_client = None

        if input_action:
            player_idx, action_type = input_action
            if action_type == "interact":
                self.handle_interaction(player_idx)

        if time.time() - self.last_spawn_time > self.spawn_interval:
            self.spawn_client()
            self.last_spawn_time = time.time()
            
        for client in self.clients:
            client.update()
            
        self.event_manager.update()
            
    def handle_interaction(self, player_idx):
        player = self.players[player_idx]
        if player.active_minigame: return
        
        for client in self.clients:
            if client.zone != player.current_zone:
                continue
                
            # Use pixel-perfect collision OR distance check
            collision = False
            
            # First check if close enough for interaction range
            distance = player.get_distance_to(client)
            if distance < TILE_SIZE * 2:
                # Then check pixel-perfect collision for precise interaction
                if player.check_collision_with(client):
                    collision = True
                elif distance < TILE_SIZE * 1.5:
                    # Allow interaction if very close even without pixel overlap
                    collision = True
                    
            if collision:
                player.current_client = client
                player.active_minigame = MiniGame(client.dish.name)
                return

    def spawn_client(self):
        zone_name = random.choice(["tacos", "kebab"])
        zone = self.world_map.get_zone(zone_name)
        
        x = random.randint(2, zone.width - 3)
        y = random.randint(4, zone.height - 2)
        
        client = Client(x * TILE_SIZE, y * TILE_SIZE, zone_name)
        self.clients.append(client)
        
    def get_remaining_time(self):
        elapsed = time.time() - self.start_time
        remaining = max(0, self.game_duration - elapsed)
        return int(remaining)
            
    def draw_zone(self, surface, camera, zone_name):
        zone = self.world_map.get_zone(zone_name)
        if zone:
            self.world_map.draw_zone(zone, surface, camera)
            
        for client in self.clients:
            if client.zone == zone_name:
                client.draw(surface, camera)
                
    def get_winner(self):
        if self.players[0].money > self.players[1].money:
            return 1
        elif self.players[1].money > self.players[0].money:
            return 2
        else:
            return 0
