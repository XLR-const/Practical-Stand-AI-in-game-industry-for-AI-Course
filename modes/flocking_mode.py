import pygame
import random
from config import (FLOCK_COUNT, FLOCK_MAX_SPEED, FLOCK_MAX_FORCE,
                    FLOCK_SEPARATION_DIST, FLOCK_NEIGHBOR_DIST,
                    FLOCK_WEIGHT_SEPARATION, FLOCK_WEIGHT_ALIGNMENT, FLOCK_WEIGHT_COHESION,
                    SCREEN_WIDTH, SCREEN_HEIGHT, NPC_SIZE, COLOR_NPC, draw_triangle,
                    WALL_VERTICAL, WALL_HORIZONTAL, handle_wall_collision)

class Boid:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * 3.14159)
        self.velocity = pygame.Vector2(pygame.math.Vector2(1, 0).rotate_rad(angle)) * FLOCK_MAX_SPEED
        self.acceleration = pygame.Vector2(0, 0)

    def apply_force(self, force):
        self.acceleration += force

    def update(self, dt):
        self.velocity += self.acceleration
        if self.velocity.length_squared() > FLOCK_MAX_SPEED**2:
            self.velocity = self.velocity.normalize() * FLOCK_MAX_SPEED
        
        old_pos = pygame.Vector2(self.pos)
        self.pos += self.velocity * dt
        self.acceleration *= 0

        self.pos = handle_wall_collision(old_pos, self.pos, NPC_SIZE // 2)

        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
        elif self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.y < 80: self.pos.y = SCREEN_HEIGHT
        elif self.pos.y > SCREEN_HEIGHT: self.pos.y = 80

class FlockingMode:
    def __init__(self, player):
        self.player = player
        self.boids = []
        random.seed(42)
        for _ in range(FLOCK_COUNT):
            x = random.randint(50, 400)
            y = random.randint(100, 700)
            self.boids.append(Boid(x, y))

    def update(self, dt):
        for boid in self.boids:
            sep = self.separation(boid) * FLOCK_WEIGHT_SEPARATION
            ali = self.alignment(boid) * FLOCK_WEIGHT_ALIGNMENT
            coh = self.cohesion(boid) * FLOCK_WEIGHT_COHESION
            avoid = self.avoid_walls(boid) * 3.0

            boid.apply_force(sep + ali + coh + avoid)
            boid.update(dt)

    def avoid_walls(self, boid):
        steer = pygame.Vector2(0, 0)
        for wall in [WALL_VERTICAL, WALL_HORIZONTAL]:
            inflated = wall.inflate(60, 60)
            if inflated.collidepoint(boid.pos.x, boid.pos.y):
                center = pygame.Vector2(wall.centerx, wall.centery)
                diff = boid.pos - center
                if diff.length_squared() > 0:
                    steer += diff.normalize() * FLOCK_MAX_SPEED
        if steer.length_squared() > 0:
            steer = steer.normalize() * FLOCK_MAX_SPEED - boid.velocity
        return steer

    def draw(self, screen):
        for boid in self.boids:
            draw_triangle(screen, boid.pos, boid.velocity, NPC_SIZE, COLOR_NPC)

    def get_info_text(self):
        return f"Алгоритм стаи | Количество противников: 30 | Здоровье игрока: {int(self.player.health)} | Агенты огибают вертикальную и горизонтальную стены"

    def separation(self, boid):
        steer = pygame.Vector2(0, 0)
        count = 0
        for other in self.boids:
            d = boid.pos.distance_to(other.pos)
            if 0 < d < FLOCK_SEPARATION_DIST:
                diff = boid.pos - other.pos
                steer += diff.normalize() / d
                count += 1
        if count > 0: steer /= count
        if steer.length_squared() > 0:
            steer = steer.normalize() * FLOCK_MAX_SPEED - boid.velocity
        return steer

    def alignment(self, boid):
        sum_vel = pygame.Vector2(0, 0)
        count = 0
        for other in self.boids:
            d = boid.pos.distance_to(other.pos)
            if 0 < d < FLOCK_NEIGHBOR_DIST:
                sum_vel += other.velocity
                count += 1
        if count > 0:
            sum_vel = (sum_vel / count).normalize() * FLOCK_MAX_SPEED
            return sum_vel - boid.velocity
        return pygame.Vector2(0, 0)

    def cohesion(self, boid):
        sum_pos = pygame.Vector2(0, 0)
        count = 0
        for other in self.boids:
            d = boid.pos.distance_to(other.pos)
            if 0 < d < FLOCK_NEIGHBOR_DIST:
                sum_pos += other.pos
                count += 1
        if count > 0:
            desired = (sum_pos / count) - boid.pos
            if desired.length_squared() > 0:
                return desired.normalize() * FLOCK_MAX_SPEED - boid.velocity
        return pygame.Vector2(0, 0)
