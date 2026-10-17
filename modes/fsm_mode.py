import pygame
import math
from config import (FSM_SPEED_PATROL, FSM_SPEED_CHASE, FSM_SPEED_RETREAT,
                    FSM_DIST_CHASE, FSM_DIST_ATTACK, FSM_DIST_PATROL,
                    FSM_HEALTH_DECREASE_DIST, FSM_HEALTH_DECREASE_RATE,
                    FSM_HEALTH_RECOVER_RATE, NPC_SIZE, COLOR_NPC, draw_triangle,
                    WALL_RECT, COLOR_WALL)

class FSMMode:
    def __init__(self, player):
        self.player = player
        self.npc_start_pos = pygame.Vector2(250, 400) # Сместили стартовую точку левее стены
        self.npc_pos = pygame.Vector2(self.npc_start_pos)
        self.npc_heading = pygame.Vector2(1, 0)
        
        self.state = "Патруль"
        self.health = 100.0
        self.patrol_angle = 0.0
        self.flash_timer = 0.0
        self.is_visible = True

    def has_line_of_sight(self):
        """Проверяет, видит ли NPC игрока (не перекрывает ли стена обзор)."""
        # Метод clipline проверяет, пересекает ли отрезок (от NPC до игрока) прямоугольник стены
        start = (int(self.npc_pos.x), int(self.npc_pos.y))
        end = (int(self.player.pos.x), int(self.player.pos.y))
        intersection = WALL_RECT.clipline(start, end)
        return len(intersection) == 0 # Если пересечений нет, значит ИИ видит игрока

    def update(self, dt):
        dist = self.npc_pos.distance_to(self.player.pos)
        can_see = self.has_line_of_sight()

        # Логика изменения здоровья
        if dist < FSM_HEALTH_DECREASE_DIST and can_see:
            self.health = max(0.0, self.health - FSM_HEALTH_DECREASE_RATE * dt)
        else:
            self.health = min(100.0, self.health + FSM_HEALTH_RECOVER_RATE * dt)

        # --- Машина состояний (FSM) с учетом видимости ---
        if self.state == "Патруль":
            # ИИ начинает погоню, только если близко И видит игрока
            if dist < FSM_DIST_CHASE and can_see:
                self.state = "Погоня"
            else:
                self.patrol_angle += 1.5 * dt
                target_x = self.npc_start_pos.x + math.cos(self.patrol_angle) * 80
                target_y = self.npc_start_pos.y + math.sin(self.patrol_angle) * 80
                target = pygame.Vector2(target_x, target_y)
                
                desired = target - self.npc_pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()
                    self.npc_pos += self.npc_heading * FSM_SPEED_PATROL * dt

        elif self.state == "Погоня":
            if self.health < 30.0:
                self.state = "Отступление"
            elif dist < FSM_DIST_ATTACK and can_see:
                self.state = "Атака"
            elif dist > FSM_DIST_CHASE or not can_see: # Если игрок скрылся за стеной — потерял след
                self.state = "Патруль"
            else:
                desired = self.player.pos - self.npc_pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()
                    self.npc_pos += self.npc_heading * FSM_SPEED_CHASE * dt

        elif self.state == "Атака":
            if self.health < 30.0:
                self.state = "Отступление"
            elif dist > FSM_DIST_ATTACK + 20 or not can_see:
                self.state = "Погоня"
            else:
                self.flash_timer += dt
                if self.flash_timer >= 0.15:
                    self.is_visible = not self.is_visible
                    self.flash_timer = 0.0
                desired = self.player.pos - self.npc_pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()

        elif self.state == "Отступление":
            if dist > FSM_DIST_PATROL:
                self.state = "Патруль"
            else:
                desired = self.npc_pos - self.player.pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()
                    # ИИ оббегает стену при отступлении (простая симуляция без сложного поиска путей)
                    self.npc_pos += self.npc_heading * FSM_SPEED_RETREAT * dt
                    
                    # Если ИИ случайно зашел внутрь стены при панике, выталкиваем его
                    if WALL_RECT.collidepoint(self.npc_pos.x, self.npc_pos.y):
                        self.npc_pos.x = WALL_RECT.left - 20

        if self.state != "Атака":
            self.is_visible = True

    def draw(self, screen):
        # Рисуем стену
        pygame.draw.rect(screen, COLOR_WALL, WALL_RECT)
        
        # Рисуем ИИ
        if self.is_visible:
            draw_triangle(screen, self.npc_pos, self.npc_heading, NPC_SIZE, COLOR_NPC)
            
        # Визуализируем радиус обнаружения (для наглядности ученикам)
        pygame.draw.circle(screen, (50, 50, 50), (int(self.npc_pos.x), int(self.npc_pos.y)), int(FSM_DIST_CHASE), width=1)

    def get_info_text(self):
        can_see_str = "ДА" if self.has_line_of_sight() else "НЕТ (За стеной)"
        return f"FSM | Состояние: {self.state} | Здоровье: {int(self.health)} | Видит игрока: {can_see_str}"
