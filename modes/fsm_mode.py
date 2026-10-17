import pygame
import math
from config import (FSM_SPEED_PATROL, FSM_SPEED_CHASE, FSM_SPEED_RETREAT,
                    FSM_DIST_CHASE, FSM_DIST_ATTACK, FSM_DIST_PATROL,
                    NPC_SIZE, COLOR_NPC, draw_triangle,
                    check_line_of_sight, handle_wall_collision)

class FSMMode:
    def __init__(self, player):
        self.player = player
        self.npc_start_pos = pygame.Vector2(200, 400)
        self.npc_pos = pygame.Vector2(self.npc_start_pos)
        self.npc_heading = pygame.Vector2(1, 0)
        self.state = "Патруль"
        self.patrol_angle = 0.0  # Вернули объявление переменной угла патрулирования!
        self.flash_timer = 0.0
        self.is_visible = True

    def update(self, dt):
        dist = self.npc_pos.distance_to(self.player.pos)
        can_see = check_line_of_sight(self.npc_pos, self.player.pos)

        old_pos = pygame.Vector2(self.npc_pos)
        
        # --- Машина состояний (FSM) ИИ ---
        if self.state == "Патруль":
            if dist < FSM_DIST_CHASE and can_see:
                self.state = "Погоня"
            else:
                self.patrol_angle += 1.5 * dt
                target = self.npc_start_pos + pygame.Vector2(math.cos(self.patrol_angle), math.sin(self.patrol_angle)) * 80
                desired = target - self.npc_pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()
                    self.npc_pos += self.npc_heading * FSM_SPEED_PATROL * dt

        elif self.state == "Погоня":
            if dist < FSM_DIST_ATTACK and can_see:
                self.state = "Атака"
            elif dist > FSM_DIST_CHASE or not can_see:
                self.state = "Патруль"
            else:
                desired = self.player.pos - self.npc_pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()
                    self.npc_pos += self.npc_heading * FSM_SPEED_CHASE * dt

        elif self.state == "Атака":
            if dist > FSM_DIST_ATTACK + 40 or not can_see:
                self.state = "Погоня"
            elif dist < 40: # Если игрок подошел вплотную, бот пугается и разрывает дистанцию
                self.state = "Отступление"
            else:
                # Нанесение урона главному герою в фазе атаки
                self.player.health = max(0.0, self.player.health - 30.0 * dt)
                
                self.flash_timer += dt
                if self.flash_timer >= 0.15:
                    self.is_visible = not self.is_visible
                    self.flash_timer = 0.0
                desired = self.player.pos - self.npc_pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()

        elif self.state == "Отступление":
            if dist > 150:
                self.state = "Погоня"
            else:
                desired = self.npc_pos - self.player.pos
                if desired.length_squared() > 0:
                    self.npc_heading = desired.normalize()
                    self.npc_pos += self.npc_heading * FSM_SPEED_RETREAT * dt

        # Физика коллизий со стенами
        self.npc_pos = handle_wall_collision(old_pos, self.npc_pos, NPC_SIZE // 2)
        if self.state != "Атака":
            self.is_visible = True

    def draw(self, screen):
        if self.is_visible:
            draw_triangle(screen, self.npc_pos, self.npc_heading, NPC_SIZE, COLOR_NPC)
        
        # Отрезок видимости ИИ (зеленый — видит, красный — обзор перекрыт стеной)
        color_line = (46, 204, 113) if check_line_of_sight(self.npc_pos, self.player.pos) else (231, 76, 60)
        pygame.draw.line(screen, color_line, self.npc_pos, self.player.pos, 1)

    def get_info_text(self):
        can_see_str = "Цель видна" if check_line_of_sight(self.npc_pos, self.player.pos) else "Цель скрыта за стенами"
        return f"Конечный автомат | Состояние противника: {self.state} | Здоровье игрока: {int(self.player.health)} | {can_see_str}"
