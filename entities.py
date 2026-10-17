import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_RADIUS, PLAYER_SPEED

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED

    def update(self, dt):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:    move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move.x += 1

        if move.length_squared() > 0:
            move = move.normalize()
            self.pos += move * self.speed * dt

        # Ограничение движения границами экрана (с учетом UI верхней панели)
        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(80 + self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))

    def draw(self, screen, color):
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), self.radius)
