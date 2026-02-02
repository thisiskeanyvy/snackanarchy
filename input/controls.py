import pygame

class InputHandler:
    def __init__(self):
        pass
        
    def handle_input(self, players, events):
        keys = pygame.key.get_pressed()
        
        # Movement
        # Player 1 (WASD)
        p1_dx, p1_dy = 0, 0
        if keys[pygame.K_w]: p1_dy = -1
        if keys[pygame.K_s]: p1_dy = 1
        if keys[pygame.K_a]: p1_dx = -1
        if keys[pygame.K_d]: p1_dx = 1
        players[0].move(p1_dx, p1_dy)
        
        # Player 2 (Arrows)
        p2_dx, p2_dy = 0, 0
        if keys[pygame.K_UP]: p2_dy = -1
        if keys[pygame.K_DOWN]: p2_dy = 1
        if keys[pygame.K_LEFT]: p2_dx = -1
        if keys[pygame.K_RIGHT]: p2_dx = 1
        players[1].move(p2_dx, p2_dy)
        
        # Interaction (E for P1, Shift/Enter/Slash for P2)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    return (0, "interact") # Player 0 interact
                if event.key == pygame.K_RSHIFT or event.key == pygame.K_RETURN:
                    return (1, "interact") # Player 1 interact
                    
        return None
