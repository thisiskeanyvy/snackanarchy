"""
Système d'animations pour SnackAnarchy
Gère les animations de sprites et les effets visuels
"""
import pygame
import math
import time
from config import *

class Animation:
    """Classe de base pour les animations"""
    
    def __init__(self, duration=1.0, loop=False):
        self.duration = duration
        self.loop = loop
        self.start_time = time.time()
        self.completed = False
        self.paused = False
        self.pause_time = 0
        
    def update(self):
        if self.paused:
            return
            
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            if self.loop:
                self.start_time = time.time()
            else:
                self.completed = True
                progress = 1.0
                
        return progress
        
    def pause(self):
        self.paused = True
        self.pause_time = time.time()
        
    def resume(self):
        if self.paused:
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration
            self.paused = False
            
    def reset(self):
        self.start_time = time.time()
        self.completed = False


class SpriteAnimation(Animation):
    """Animation de sprite avec plusieurs frames"""
    
    def __init__(self, frames, frame_duration=0.1, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        super().__init__(duration=len(frames) * frame_duration, loop=loop)
        
    def update(self):
        progress = super().update()
        if progress is not None:
            self.current_frame = int(progress * len(self.frames))
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1
        return self.get_current_frame()
        
    def get_current_frame(self):
        return self.frames[self.current_frame]


class WalkAnimation(Animation):
    """Animation de marche avec bobbing"""
    
    def __init__(self, base_image, direction='right'):
        super().__init__(duration=0.4, loop=True)
        self.base_image = base_image
        self.direction = direction
        self.bob_amplitude = 3
        self.is_walking = False
        
    def update(self, is_moving=False):
        self.is_walking = is_moving
        if not is_moving:
            return self.base_image, 0
            
        progress = super().update()
        if progress is None:
            progress = 0
            
        # Mouvement de bobbing sinusoïdal
        bob_offset = math.sin(progress * math.pi * 2) * self.bob_amplitude
        return self.base_image, bob_offset


class AttackAnimation(Animation):
    """Animation d'attaque (coup de couteau/fourchette)"""
    
    def __init__(self, attacker_pos, target_pos, weapon_type='knife'):
        super().__init__(duration=0.3, loop=False)
        self.attacker_pos = attacker_pos
        self.target_pos = target_pos
        self.weapon_type = weapon_type
        self.current_pos = list(attacker_pos)
        self.hit_frame = False
        
    def update(self):
        progress = super().update()
        if progress is None:
            return None
            
        # Phase 1: Lever l'arme (0-30%)
        # Phase 2: Frapper (30-60%)
        # Phase 3: Retour (60-100%)
        
        if progress < 0.3:
            # Préparation - léger recul
            t = progress / 0.3
            offset = -10 * t
            self.current_pos[0] = self.attacker_pos[0] + offset
            
        elif progress < 0.6:
            # Frappe rapide vers la cible
            t = (progress - 0.3) / 0.3
            dx = self.target_pos[0] - self.attacker_pos[0]
            dy = self.target_pos[1] - self.attacker_pos[1]
            self.current_pos[0] = self.attacker_pos[0] + dx * t * 0.8
            self.current_pos[1] = self.attacker_pos[1] + dy * t * 0.8
            
            if progress >= 0.5 and not self.hit_frame:
                self.hit_frame = True
                
        else:
            # Retour
            t = (progress - 0.6) / 0.4
            dx = self.target_pos[0] - self.attacker_pos[0]
            dy = self.target_pos[1] - self.attacker_pos[1]
            self.current_pos[0] = self.attacker_pos[0] + dx * 0.8 * (1 - t)
            self.current_pos[1] = self.attacker_pos[1] + dy * 0.8 * (1 - t)
            
        return {
            'pos': tuple(self.current_pos),
            'hit': self.hit_frame and progress >= 0.5 and progress < 0.6,
            'progress': progress
        }
        
    def draw_weapon(self, surface, camera):
        """Dessine l'arme pendant l'animation"""
        draw_x = self.current_pos[0] - camera.x
        draw_y = self.current_pos[1] - camera.y
        
        # Angle de l'arme
        dx = self.target_pos[0] - self.attacker_pos[0]
        dy = self.target_pos[1] - self.attacker_pos[1]
        angle = math.atan2(dy, dx)
        
        if self.weapon_type == 'knife':
            color = (180, 180, 180)
            length = 25
        else:  # fork
            color = (150, 150, 150)
            length = 30
            
        end_x = draw_x + math.cos(angle) * length
        end_y = draw_y + math.sin(angle) * length
        
        pygame.draw.line(surface, color, (draw_x, draw_y), (end_x, end_y), 4)
        
        # Pointe de l'arme
        if self.weapon_type == 'knife':
            pygame.draw.circle(surface, (200, 200, 200), (int(end_x), int(end_y)), 3)
        else:
            # Dents de la fourchette
            for offset in [-5, 0, 5]:
                prong_x = end_x + math.cos(angle) * 8
                prong_y = end_y + math.sin(angle) * 8 + offset
                pygame.draw.line(surface, color, (end_x, end_y + offset), (prong_x, prong_y), 2)


class StealAnimation(Animation):
    """Animation de vol de broche"""
    
    def __init__(self, thief_pos, target_pos):
        super().__init__(duration=1.0, loop=False)
        self.thief_pos = thief_pos
        self.target_pos = target_pos
        self.spit_pos = list(target_pos)
        self.phase = 'reach'  # reach, grab, retreat
        
    def update(self):
        progress = super().update()
        if progress is None:
            return None
            
        if progress < 0.4:
            # Phase: Atteindre la broche
            self.phase = 'reach'
            t = progress / 0.4
            # Main qui s'étend
            
        elif progress < 0.6:
            # Phase: Saisir
            self.phase = 'grab'
            
        else:
            # Phase: Retrait avec la broche
            self.phase = 'retreat'
            t = (progress - 0.6) / 0.4
            # La broche suit le voleur
            dx = self.thief_pos[0] - self.target_pos[0]
            dy = self.thief_pos[1] - self.target_pos[1]
            self.spit_pos[0] = self.target_pos[0] + dx * t
            self.spit_pos[1] = self.target_pos[1] + dy * t
            
        return {
            'phase': self.phase,
            'spit_pos': tuple(self.spit_pos),
            'progress': progress
        }


class DeathAnimation(Animation):
    """Animation de mort d'un client"""
    
    def __init__(self, position, death_type='stab'):
        super().__init__(duration=0.8, loop=False)
        self.position = list(position)
        self.death_type = death_type
        self.rotation = 0
        self.alpha = 255
        self.blood_particles = []
        
        # Créer des particules de sang
        for _ in range(8):
            import random
            self.blood_particles.append({
                'x': position[0],
                'y': position[1],
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-5, -1),
                'size': random.randint(3, 8),
                'alpha': 255
            })
            
    def update(self):
        progress = super().update()
        if progress is None:
            return None
            
        # Rotation et chute
        self.rotation = progress * 90  # Tombe sur le côté
        self.position[1] += progress * 2  # Légère chute
        self.alpha = int(255 * (1 - progress * 0.5))  # Fade léger
        
        # Mise à jour des particules de sang
        for p in self.blood_particles:
            p['vy'] += 0.3  # Gravité
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] = max(0, int(255 * (1 - progress)))
            
        return {
            'position': tuple(self.position),
            'rotation': self.rotation,
            'alpha': self.alpha,
            'particles': self.blood_particles,
            'progress': progress
        }
        
    def draw(self, surface, camera, original_image):
        """Dessine l'animation de mort"""
        data = self.update()
        if data is None:
            return
            
        draw_x = data['position'][0] - camera.x
        draw_y = data['position'][1] - camera.y
        
        # Dessiner les particules de sang d'abord (derrière)
        # Compatible macOS: utiliser set_alpha() au lieu de couleur RGBA
        for p in data['particles']:
            if p['alpha'] > 0:
                px = p['x'] - camera.x
                py = p['y'] - camera.y
                size = max(2, p['size'])
                blood_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                blood_surface.fill((0, 0, 0, 0))  # Transparent
                pygame.draw.circle(blood_surface, (180, 0, 0), 
                                 (size//2, size//2), size//2)
                blood_surface.set_alpha(p['alpha'])
                surface.blit(blood_surface, (int(px), int(py)))
        
        # Dessiner le sprite avec rotation et transparence
        if original_image:
            rotated = pygame.transform.rotate(original_image, -data['rotation'])
            rotated_copy = rotated.copy()
            rotated_copy.set_alpha(data['alpha'])
            rect = rotated_copy.get_rect(center=(draw_x + original_image.get_width()//2, 
                                            draw_y + original_image.get_height()//2))
            surface.blit(rotated_copy, rect)


class FleeAnimation(Animation):
    """Animation de fuite d'un client effrayé"""
    
    def __init__(self, start_pos, direction='right'):
        super().__init__(duration=1.5, loop=False)
        self.start_pos = list(start_pos)
        self.current_pos = list(start_pos)
        self.direction = 1 if direction == 'right' else -1
        self.speed = 8
        self.wobble = 0
        
    def update(self):
        progress = super().update()
        if progress is None:
            return None
            
        # Mouvement paniqué
        self.current_pos[0] += self.speed * self.direction
        self.wobble = math.sin(progress * 20) * 5
        self.current_pos[1] = self.start_pos[1] + self.wobble
        
        return {
            'position': tuple(self.current_pos),
            'wobble': self.wobble,
            'progress': progress
        }


class PickupAnimation(Animation):
    """Animation de ramassage d'objet"""
    
    def __init__(self, item_pos, player_pos):
        super().__init__(duration=0.3, loop=False)
        self.item_pos = list(item_pos)
        self.player_pos = player_pos
        self.scale = 1.0
        
    def update(self):
        progress = super().update()
        if progress is None:
            return None
            
        # L'objet se déplace vers le joueur en rétrécissant
        t = progress
        self.item_pos[0] = self.item_pos[0] + (self.player_pos[0] - self.item_pos[0]) * t * 0.3
        self.item_pos[1] = self.item_pos[1] + (self.player_pos[1] - self.item_pos[1]) * t * 0.3
        self.scale = 1.0 - progress * 0.5
        
        return {
            'position': tuple(self.item_pos),
            'scale': self.scale,
            'progress': progress
        }


class FloatingText(Animation):
    """Animation de texte flottant (ex: +20€, -5 réputation)"""
    
    def __init__(self, text, position, color=WHITE, font_size=24):
        super().__init__(duration=1.5, loop=False)
        self.text = text
        self.position = list(position)
        self.color = color
        self.font_size = font_size
        self.alpha = 255
        
    def update(self):
        progress = super().update()
        if progress is None:
            return None
            
        # Monte et disparaît
        self.position[1] -= 1
        self.alpha = int(255 * (1 - progress))
        
        return {
            'text': self.text,
            'position': tuple(self.position),
            'alpha': self.alpha,
            'progress': progress
        }
        
    def draw(self, surface, camera):
        data = self.update()
        if data is None or data['alpha'] <= 0:
            return
            
        draw_x = data['position'][0] - camera.x
        draw_y = data['position'][1] - camera.y
        
        font = pygame.font.SysFont(None, self.font_size)
        text_surface = font.render(data['text'], True, self.color)
        text_surface.set_alpha(data['alpha'])
        surface.blit(text_surface, (draw_x, draw_y))


class ServeAnimation(Animation):
    """
    Animation de service : le joueur va à la cuisine puis revient vers le client pour servir.
    Phase 1: déplacement vers la cuisine
    Phase 2: déplacement retour vers le client
    Phase 3: courte pause (geste de servir)
    """

    def __init__(self, start_pos, kitchen_pos, client_pos, duration=1.4):
        super().__init__(duration=duration, loop=False)
        self.start_pos = list(start_pos)
        self.kitchen_pos = list(kitchen_pos)
        self.client_pos = list(client_pos)
        self.current_pos = list(start_pos)
        # Répartition: 0.5s aller cuisine, 0.5s retour client, 0.4s pause
        self.phase1_end = 0.5
        self.phase2_end = 1.0

    def update(self):
        progress = super().update()
        if progress is None:
            return self.current_pos

        if progress >= 1.0:
            self.current_pos[0] = self.client_pos[0]
            self.current_pos[1] = self.client_pos[1]
            return self.current_pos

        if progress < self.phase1_end:
            # Phase 1 : aller vers la cuisine
            t = progress / self.phase1_end
            t = t * t * (3 - 2 * t)  # smoothstep
            self.current_pos[0] = self.start_pos[0] + (self.kitchen_pos[0] - self.start_pos[0]) * t
            self.current_pos[1] = self.start_pos[1] + (self.kitchen_pos[1] - self.start_pos[1]) * t
        elif progress < self.phase2_end:
            # Phase 2 : revenir vers le client
            t = (progress - self.phase1_end) / (self.phase2_end - self.phase1_end)
            t = t * t * (3 - 2 * t)
            self.current_pos[0] = self.kitchen_pos[0] + (self.client_pos[0] - self.kitchen_pos[0]) * t
            self.current_pos[1] = self.kitchen_pos[1] + (self.client_pos[1] - self.kitchen_pos[1]) * t
        else:
            # Phase 3 : rester sur le client
            self.current_pos[0] = self.client_pos[0]
            self.current_pos[1] = self.client_pos[1]

        return self.current_pos


def _thief_zone_positions(zone_name):
    """Retourne (spawn_x, spawn_y, register_x, register_y) en pixels pour la zone restaurant."""
    from config import TILE_SIZE, RESTAURANT_WIDTH, RESTAURANT_HEIGHT
    # Porte en bas au centre
    door_tile_x = RESTAURANT_WIDTH // 2
    door_tile_y = RESTAURANT_HEIGHT - 1
    spawn_x = door_tile_x * TILE_SIZE
    spawn_y = door_tile_y * TILE_SIZE
    # Caisse devant le comptoir (au centre, rangée du haut)
    register_tile_x = RESTAURANT_WIDTH // 2
    register_tile_y = 2
    register_x = register_tile_x * TILE_SIZE
    register_y = register_tile_y * TILE_SIZE
    return spawn_x, spawn_y, register_x, register_y


class ThiefAnimation(Animation):
    """
    Animation du voleur : spawn à la porte du restaurant adverse, va à la caisse,
    vole, puis ressort par la porte.
    """
    def __init__(self, zone_name, duration=2.8):
        super().__init__(duration=duration, loop=False)
        self.zone_name = zone_name
        self.spawn_x, self.spawn_y, self.register_x, self.register_y = _thief_zone_positions(zone_name)
        self.current_pos = [float(self.spawn_x), float(self.spawn_y)]
        self.facing_right = True

    def update(self):
        progress = super().update()
        if progress is None:
            return None
        # Phase 0-0.35 : marcher de la porte vers la caisse
        # Phase 0.35-0.55 : rester à la caisse (vol)
        # Phase 0.55-1.0 : marcher de la caisse vers la porte
        if progress < 0.35:
            t = progress / 0.35
            t = t * t * (3 - 2 * t)
            self.current_pos[0] = self.spawn_x + (self.register_x - self.spawn_x) * t
            self.current_pos[1] = self.spawn_y + (self.register_y - self.spawn_y) * t
            self.facing_right = self.register_x >= self.spawn_x
        elif progress < 0.55:
            self.current_pos[0] = self.register_x
            self.current_pos[1] = self.register_y
        else:
            t = (progress - 0.55) / 0.45
            t = t * t * (3 - 2 * t)
            self.current_pos[0] = self.register_x + (self.spawn_x - self.register_x) * t
            self.current_pos[1] = self.register_y + (self.spawn_y - self.register_y) * t
            self.facing_right = self.spawn_x >= self.register_x
        return {
            'position': (int(self.current_pos[0]), int(self.current_pos[1])),
            'facing_right': self.facing_right,
            'progress': progress,
        }

    def draw(self, surface, camera):
        data = self.update()
        if data is None:
            return
        from game.assets_loader import Assets
        img = Assets.get().get_image("voleur")
        if not img:
            return
        if not data['facing_right']:
            img = pygame.transform.flip(img, True, False)
        draw_x = data['position'][0] - camera.x
        draw_y = data['position'][1] - camera.y
        surface.blit(img, (draw_x, draw_y))


class AnimationManager:
    """Gestionnaire global des animations"""
    
    def __init__(self):
        self.animations = []
        self.floating_texts = []
        
    def add_animation(self, animation):
        self.animations.append(animation)
        
    def add_floating_text(self, text, position, color=WHITE, font_size=24):
        self.floating_texts.append(FloatingText(text, position, color, font_size))
        
    def update(self):
        # Mettre à jour et nettoyer les animations terminées
        self.animations = [a for a in self.animations if not a.completed]
        for anim in self.animations:
            anim.update()
            
        self.floating_texts = [t for t in self.floating_texts if not t.completed]
        for text in self.floating_texts:
            text.update()
            
    def draw(self, surface, camera):
        for text in self.floating_texts:
            text.draw(surface, camera)
            
    def clear(self):
        self.animations.clear()
        self.floating_texts.clear()
