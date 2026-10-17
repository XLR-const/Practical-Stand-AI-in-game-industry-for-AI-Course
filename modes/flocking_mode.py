import pygame
import random
import math
from config import (FLOCK_COUNT, FLOCK_MAX_SPEED, FLOCK_MAX_FORCE,
                    FLOCK_SEPARATION_DIST, FLOCK_NEIGHBOR_DIST,
                    FLOCK_WEIGHT_ALIGNMENT, FLOCK_WEIGHT_COHESION,
                    SCREEN_WIDTH, SCREEN_HEIGHT, NPC_SIZE, COLOR_NPC, draw_triangle,
                    WALL_VERTICAL, WALL_HORIZONTAL, handle_wall_collision, check_line_of_sight)

class Boid:
    def __init__(self, x, y, index):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * 3.14159)
        self.velocity = pygame.Vector2(pygame.math.Vector2(1, 0).rotate_rad(angle)) * FLOCK_MAX_SPEED
        self.acceleration = pygame.Vector2(0, 0)
        
        # Стабильный вектор взгляда, независимый от вибраций скорости
        self.render_heading = pygame.Vector2(pygame.math.Vector2(1, 0).rotate_rad(angle))
        self.attack_offset_angle = (2 * math.pi / FLOCK_COUNT) * index

    def apply_force(self, force):
        self.acceleration += force

    def update(self, dt):
        self.velocity += self.acceleration
        if self.velocity.length_squared() > FLOCK_MAX_SPEED**2:
            self.velocity = self.velocity.normalize() * FLOCK_MAX_SPEED
        
        old_pos = pygame.Vector2(self.pos)
        self.pos += self.velocity * dt
        self.acceleration *= 0

        # Физическое скольжение по граням стен
        self.pos = handle_wall_collision(old_pos, self.pos, NPC_SIZE // 2)

        # Мягкий отскок от границ экрана
        margin = NPC_SIZE // 2
        if self.pos.x < margin:
            self.pos.x = margin
            self.velocity.x *= -1
        elif self.pos.x > SCREEN_WIDTH - margin:
            self.pos.x = SCREEN_WIDTH - margin
            self.velocity.x *= -1
            
        if self.pos.y < 80 + margin:
            self.pos.y = 80 + margin
            self.velocity.y *= -1
        elif self.pos.y > SCREEN_HEIGHT - margin:
            self.pos.y = SCREEN_HEIGHT - margin
            self.velocity.y *= -1

class FlockingMode:
    def __init__(self, player):
        self.player = player
        self.boids = []
        self.smoothed_status = "Патрулирование стаи"
        self.status_lock_timer = 0.0
        
        random.seed(42)
        for i in range(FLOCK_COUNT):
            x = random.randint(50, 350)
            y = random.randint(100, 700)
            self.boids.append(Boid(x, y, i))

    def update(self, dt):
        self.status_lock_timer += dt

        for boid in self.boids:
            dist_to_player = boid.pos.distance_to(self.player.pos)
            sep_weight = 5.0 if dist_to_player < 150 else 1.8

            sep = self.separation(boid) * sep_weight
            ali = self.alignment(boid) * FLOCK_WEIGHT_ALIGNMENT
            coh = self.cohesion(boid) * FLOCK_WEIGHT_COHESION
            avoid_inner = self.avoid_walls(boid) * 3.5
            avoid_edges = self.avoid_screen_edges(boid) * 2.0
            chase_or_flee = self.player_interaction(boid)

            # ГРАФИЧЕСКОЕ ИСПРАВЛЕНИЕ: Вычисляем чистый вектор взгляда ИИ.
            # Если рой атакует, боты смотрят СТРОГО на игрока (или по курсу),
            # полностью игнорируя дикие микро-вибрации силы расталкивания (Separation).
            if chase_or_flee.length_squared() > 0:
                boid.render_heading = (self.player.pos - boid.pos).normalize()
            elif boid.velocity.length_squared() > 10.0:
                boid.render_heading = boid.velocity.normalize()

            boid.apply_force(sep + ali + coh + avoid_inner + avoid_edges + chase_or_flee)
            boid.update(dt)

            # Стабильное нанесение урона по ГГ
            if boid.pos.distance_to(self.player.pos) < 45:
                self.player.health = max(0.0, self.player.health - 65.0 * dt)

        if self.status_lock_timer >= 0.15:
            self.status_lock_timer = 0.0
            self.update_smoothed_status()

    def player_interaction(self, boid):
        dist = boid.pos.distance_to(self.player.pos)
        can_see = check_line_of_sight(boid.pos, self.player.pos)
        
        if not can_see:
            return pygame.Vector2(0, 0)

        if dist < 450:
            target_offset = pygame.Vector2(math.cos(boid.attack_offset_angle), math.sin(boid.attack_offset_angle)) * 38
            target_pos = self.player.pos + target_offset
            desired = target_pos - boid.pos
            if desired.length_squared() > 0:
                return desired.normalize() * FLOCK_MAX_SPEED * 1.4 - boid.velocity
            
        return pygame.Vector2(0, 0)

    def avoid_walls(self, boid):
        steer = pygame.Vector2(0, 0)
        for wall in [WALL_VERTICAL, WALL_HORIZONTAL]:
            inflated = wall.inflate(70, 70)
            if inflated.collidepoint(boid.pos.x, boid.pos.y):
                center = pygame.Vector2(wall.centerx, wall.centery)
                diff = boid.pos - center
                if diff.length_squared() > 0:
                    steer += diff.normalize() * FLOCK_MAX_SPEED
        if steer.length_squared() > 0:
            steer = steer.normalize() * FLOCK_MAX_SPEED - boid.velocity
            if steer.length_squared() > FLOCK_MAX_FORCE**2:
                steer = steer.normalize() * FLOCK_MAX_FORCE
        return steer

    def avoid_screen_edges(self, boid):
        steer = pygame.Vector2(0, 0)
        margin = 60
        if boid.pos.x < margin:
            steer.x = FLOCK_MAX_SPEED
        elif boid.pos.x > SCREEN_WIDTH - margin:
            steer.x = -FLOCK_MAX_SPEED
            
        if boid.pos.y < 80 + margin:
            steer.y = FLOCK_MAX_SPEED
        elif boid.pos.y > SCREEN_HEIGHT - margin:
            steer.y = -FLOCK_MAX_SPEED

        if steer.length_squared() > 0:
            steer = steer.normalize() * FLOCK_MAX_SPEED - boid.velocity
            if steer.length_squared() > FLOCK_MAX_FORCE**2:
                steer = steer.normalize() * FLOCK_MAX_FORCE
        return steer

    def update_smoothed_status(self):
        active_chasers = sum(1 for b in self.boids if check_line_of_sight(b.pos, self.player.pos) and b.pos.distance_to(self.player.pos) < 450)
        if active_chasers > 0:
            if any(b.pos.distance_to(self.player.pos) < 50 for b in self.boids):
                self.smoothed_status = f"Атака роя (Противники зажали игрока!)"
            else:
                self.smoothed_status = f"Атака роя ({active_chasers} противников преследуют цель)"
        else:
            self.smoothed_status = "Патрулирование стаи"

    def draw(self, screen):
        for boid in self.boids:
            # Отрисовываем ГАРАНТИРОВАННО ровные треугольники по отфильтрованному вектору взгляда boid.render_heading
            draw_triangle(screen, boid.pos, boid.render_heading, NPC_SIZE, COLOR_NPC)

    def get_info_text(self):
        return f"Алгоритм стаи | Количество противников: {FLOCK_COUNT} | Здоровье игрока: {int(self.player.health)} | Режим роя: {self.smoothed_status}"

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
            desired = (sum_pos / count) - boid.pos
            if desired.length_squared() > 0:
                steer = desired.normalize() * FLOCK_MAX_SPEED - boid.velocity
                if steer.length_squared() > FLOCK_MAX_FORCE**2:
                    steer = steer.normalize() * FLOCK_MAX_FORCE
                return steer
        return pygame.Vector2(0, 0)
