import pygame
import random
from config import (FLOCK_COUNT, FLOCK_MAX_SPEED, FLOCK_MAX_FORCE,
                    FLOCK_SEPARATION_DIST, FLOCK_NEIGHBOR_DIST,
                    FLOCK_WEIGHT_SEPARATION, FLOCK_WEIGHT_ALIGNMENT, FLOCK_WEIGHT_COHESION,
                    SCREEN_WIDTH, SCREEN_HEIGHT, NPC_SIZE, COLOR_NPC, draw_triangle)

class Boid:
    """Класс отдельного агента стаи (Boid)."""
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        # Случайное начальное направление движения
        angle = random.uniform(0, 2 * 3.14159)
        self.velocity = pygame.Vector2(pygame.math.Vector2(1, 0).rotate_rad(angle)) * FLOCK_MAX_SPEED
        self.acceleration = pygame.Vector2(0, 0)

    def apply_force(self, force):
        self.acceleration += force

    def update(self, dt):
        self.velocity += self.acceleration
        if self.velocity.length_squared() > FLOCK_MAX_SPEED**2:
            self.velocity = self.velocity.normalize() * FLOCK_MAX_SPEED
        
        self.pos += self.velocity * dt
        self.acceleration *= 0 # Сброс ускорения на каждом кадре

        # Мягкие границы: телепортация агентов при вылете за экран
        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
        elif self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.y < 80: self.pos.y = SCREEN_HEIGHT
        elif self.pos.y > SCREEN_HEIGHT: self.pos.y = 80

class FlockingMode:
    def __init__(self, player):
        self.player = player
        self.boids = []
        
        # Детерминированный спавн стаи
        random.seed(42)
        for _ in range(FLOCK_COUNT):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(150, SCREEN_HEIGHT - 100)
            self.boids.append(Boid(x, y))

    def update(self, dt):
        for boid in self.boids:
            # Вычисление трех базовых сил поведения стаи
            sep = self.separation(boid)
            ali = self.alignment(boid)
            coh = self.cohesion(boid)

            # Взвешивание сил
            sep *= FLOCK_WEIGHT_SEPARATION
            ali *= FLOCK_WEIGHT_ALIGNMENT
            coh *= FLOCK_WEIGHT_COHESION

            # Применение сил к агенту
            boid.apply_force(sep)
            boid.apply_force(ali)
            boid.apply_force(coh)
            
            boid.update(dt)

    def draw(self, screen):
        for boid in self.boids:
            draw_triangle(screen, boid.pos, boid.velocity, NPC_SIZE, COLOR_NPC)

    def get_info_text(self):
        return f"Flocking: {FLOCK_COUNT} NPC | Разделение: {FLOCK_WEIGHT_SEPARATION} | Выравнивание: {FLOCK_WEIGHT_ALIGNMENT} | Сплочение: {FLOCK_WEIGHT_COHESION}"

    # --- Реализация алгоритмов Рейнольдса ---
    def separation(self, boid):
        steer = pygame.Vector2(0, 0)
        count = 0
        for other in self.boids:
            d = boid.pos.distance_to(other.pos)
            if 0 < d < FLOCK_SEPARATION_DIST:
                diff = boid.pos - other.pos
                diff = diff.normalize() / d # Сила обратно пропорциональна расстоянию
                steer += diff
                count += 1
        if count > 0:
            steer /= count
        if steer.length_squared() > 0:
            steer = steer.normalize() * FLOCK_MAX_SPEED - boid.velocity
            if steer.length_squared() > FLOCK_MAX_FORCE**2:
                steer = steer.normalize() * FLOCK_MAX_FORCE
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
            sum_vel /= count
            sum_vel = sum_vel.normalize() * FLOCK_MAX_SPEED
            steer = sum_vel - boid.velocity
            if steer.length_squared() > FLOCK_MAX_FORCE**2:
                steer = steer.normalize() * FLOCK_MAX_FORCE
            return steer
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
            sum_pos /= count
            desired = sum_pos - boid.pos
            if desired.length_squared() > 0:
                desired = desired.normalize() * FLOCK_MAX_SPEED
                steer = desired - boid.velocity
                if steer.length_squared() > FLOCK_MAX_FORCE**2:
                    steer = steer.normalize() * FLOCK_MAX_FORCE
                return steer
        return pygame.Vector2(0, 0)
