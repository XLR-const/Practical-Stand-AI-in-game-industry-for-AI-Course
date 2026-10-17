import pygame
import math
import random
from config import (MARKOV_INTERVAL, MARKOV_MATRIX, NPC_SIZE,
                    COLOR_NPC, draw_triangle, check_line_of_sight, 
                    handle_wall_collision, WALL_VERTICAL, WALL_HORIZONTAL)

class MarkovMode:
    def __init__(self, player):
        self.player = player
        # Точка центра зоны патрулирования (внутри безопасного сектора за стенами)
        self.patrol_center = pygame.Vector2(250, 300)
        # Точка для ведения огня (выход на атакующую позицию)
        self.firing_pos = pygame.Vector2(530, 430)
        
        self.npc_pos = pygame.Vector2(self.patrol_center)
        self.npc_heading = pygame.Vector2(0, -1)
        
        # Заменили статичное "Укрытие" на динамичное "Патрулирование"
        self.state = "Патрулирование"
        self.state_timer = 0.0
        self.patrol_angle = 0.0
        
        self.stats = {"Стрельба": 0, "Граната": 0}
        self.flash_timer = 0.0
        self.current_color = COLOR_NPC

    def update(self, dt):
        can_see = check_line_of_sight(self.npc_pos, self.player.pos)
        
        # ЕСЛИ ИГРОК ЗА СТЕНАМИ: Принудительно заставляем ИИ патрулировать в безопасности
        if not can_see:
            self.state = "Патрулирование"
            self.state_timer = 0.0  # Замораживаем марковский таймер переключения
        else:
            # Если игрок на виду — работает стандартный марковский выбор случайных атак
            self.state_timer += dt
            if self.state_timer >= MARKOV_INTERVAL:
                self.state_timer = 0.0
                self.transition_to_next_state()

        old_pos = pygame.Vector2(self.npc_pos)
        self.flash_timer += dt
        
        # --- Логика перемещения, поворота головы и урона по состояниям ---
        if self.state == "Патрулирование":
            self.current_color = COLOR_NPC
            
            # Поворот головы: ИИ НЕ крутится за игроком сквозь стену, а смотрит по вектору своего движения
            self.patrol_angle += 2.0 * dt
            target = self.patrol_center + pygame.Vector2(math.cos(self.patrol_angle), math.sin(self.patrol_angle)) * 70
            desired = target - self.npc_pos
            if desired.length_squared() > 0:
                self.npc_heading = desired.normalize()
                self.npc_pos += self.npc_heading * 120 * dt # Движение по кругу патрулирования
                
        elif self.state == "Стрельба":
            # Поворот головы: Направлен строго на игрока, так как цель видна
            desired = self.player.pos - self.npc_pos
            if desired.length_squared() > 0:
                self.npc_heading = desired.normalize()

            # Выдвижение на огневую позицию из-за угла стен
            move_dir = self.firing_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 160 * dt
                
            if self.flash_timer >= 0.1:
                self.current_color = (255, 100, 100) if self.current_color == COLOR_NPC else COLOR_NPC
                self.flash_timer = 0.0
                
            # Нанесение урона лазером
            if can_see:
                self.player.health = max(0.0, self.player.health - 40.0 * dt)
                
        elif self.state == "Граната":
            # Поворот головы направлен на игрока
            desired = self.player.pos - self.npc_pos
            if desired.length_squared() > 0:
                self.npc_heading = desired.normalize()

            # Выдвижение на атакующую позицию
            move_dir = self.firing_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 160 * dt
                
            if self.flash_timer >= 0.1:
                self.current_color = (241, 196, 15) if self.current_color == (230, 126, 34) else (230, 126, 34)
                self.flash_timer = 0.0
                
            # Нанесение урона гранатой по площади
            if can_see and self.npc_pos.distance_to(self.player.pos) < 500:
                # Проверяем, находится ли игрок в радиусе взрыва (60 пикселей)
                mouse_dist = self.player.pos.distance_to(self.player.pos) # Игрок всегда в эпицентре своей позиции
                self.player.health = max(0.0, self.player.health - 50.0 * dt)

        # Обработка физических столкновений со всеми стенами на карте
        self.npc_pos = handle_wall_collision(old_pos, self.npc_pos, NPC_SIZE // 2)

    def transition_to_next_state(self):
        # Матрица переходов (Переименовали "Укрытие" в "Патрулирование" для логики кода)
        probabilities = MARKOV_MATRIX["Укрытие" if self.state == "Патрулирование" else self.state]
        rand_val = random.random()
        cum_sum = 0.0
        next_state = self.state
        states_pool = ["Патрулирование", "Стрельба", "Граната"]
        
        for idx, prob in enumerate(probabilities):
            cum_sum += prob
            if rand_val <= cum_sum:
                next_state = states_pool[idx]
                break
                
        self.state = next_state
        if self.state in self.stats:
            self.stats[self.state] += 1

    def draw(self, screen):
        # Отрисовка треугольника ИИ
        draw_triangle(screen, self.npc_pos, self.npc_heading, NPC_SIZE, self.current_color)
        can_see = check_line_of_sight(self.npc_pos, self.player.pos)
        
        # Эффекты визуализации боевых действий
        if self.state == "Стрельба" and can_see:
            pygame.draw.line(screen, (255, 0, 0), self.npc_pos, self.player.pos, 2)
        elif self.state == "Граната" and can_see:
            pygame.draw.circle(screen, (241, 196, 15), (int(self.player.pos.x), int(self.player.pos.y)), 60, width=2)

    def get_info_text(self):
        can_see_str = "Цель видна" if check_line_of_sight(self.npc_pos, self.player.pos) else "Цель скрыта за стенами (ИИ ушел в патрулирование)"
        return f"Цепи Маркова | Состояние противника: {self.state} | Здоровье игрока: {int(self.player.health)} | Всего вызовов -> Стрельба: {self.stats['Стрельба']}, Граната: {self.stats['Граната']} | {can_see_str}"
