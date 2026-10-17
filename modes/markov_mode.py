import pygame
import random
from config import (MARKOV_INTERVAL, MARKOV_MATRIX, NPC_SIZE,
                    COLOR_NPC, draw_triangle, check_line_of_sight, handle_wall_collision)

class MarkovMode:
    def __init__(self, player):
        self.player = player
        # Точка "безопасного кармана" за стыком двух стен
        self.hiding_pos = pygame.Vector2(410, 310)
        # Точка для атаки (выходит на оперативный простор)
        self.firing_pos = pygame.Vector2(530, 430)
        
        self.npc_pos = pygame.Vector2(self.hiding_pos)
        self.npc_heading = pygame.Vector2(0, -1)
        self.state = "Укрытие"
        self.state_timer = 0.0
        self.stats = {"Стрельба": 0, "Граната": 0}
        
        self.flash_timer = 0.0
        self.current_color = COLOR_NPC

    def update(self, dt):
        self.state_timer += dt
        
        desired = self.player.pos - self.npc_pos
        if desired.length_squared() > 0:
            self.npc_heading = desired.normalize()

        if self.state_timer >= MARKOV_INTERVAL:
            self.state_timer = 0.0
            self.transition_to_next_state()

        old_pos = pygame.Vector2(self.npc_pos)
        self.flash_timer += dt
        
        if self.state == "Укрытие":
            self.current_color = COLOR_NPC
            # ИИ уходит глубоко в укрытие за угол стен
            move_dir = self.hiding_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 160 * dt
                
        elif self.state == "Стрельба":
            # ИИ выходит на атакующую позицию
            move_dir = self.firing_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 160 * dt
            if self.flash_timer >= 0.1:
                self.current_color = (255, 100, 100) if self.current_color == COLOR_NPC else COLOR_NPC
                self.flash_timer = 0.0
                
        elif self.state == "Граната":
            # ИИ выходит на атакующую позицию
            move_dir = self.firing_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 160 * dt
            if self.flash_timer >= 0.1:
                self.current_color = (241, 196, 15) if self.current_color == (230, 126, 34) else (230, 126, 34)
                self.flash_timer = 0.0

        # Страховочная проверка коллизий
        self.npc_pos = handle_wall_collision(old_pos, self.npc_pos, NPC_SIZE // 2)

    def transition_to_next_state(self):
        probabilities = MARKOV_MATRIX[self.state]
        rand_val = random.random()
        cum_sum = 0.0
        next_state = self.state
        states_pool = ["Укрытие", "Стрельба", "Граната"]
        
        for idx, prob in enumerate(probabilities):
            cum_sum += prob
            if rand_val <= cum_sum:
                next_state = states_pool[idx]
                break
                
        self.state = next_state
        if self.state in self.stats:
            self.stats[self.state] += 1

    def draw(self, screen):
        draw_triangle(screen, self.npc_pos, self.npc_heading, NPC_SIZE, self.current_color)
        
        # Проверяем видимость: атакующие действия срабатывают, только если ИИ физически видит цель
        can_see = check_line_of_sight(self.npc_pos, self.player.pos)
        
        if self.state == "Стрельба":
            if can_see:
                pygame.draw.line(screen, (255, 0, 0), self.npc_pos, self.player.pos, 2)
            else:
                # Луч упирается в стену, если игрок спрятался
                pygame.draw.line(screen, (100, 50, 50), self.npc_pos, self.npc_pos + self.npc_heading * 150, 1)
        elif self.state == "Граната" and can_see:
            pygame.draw.circle(screen, (241, 196, 15), (int(self.player.pos.x), int(self.player.pos.y)), 60, width=2)

    def get_info_text(self):
        can_see_str = "Цель видна" if check_line_of_sight(self.npc_pos, self.player.pos) else "Цель скрыта за стенами"
        return f"Markov | Состояние: {self.state} | {can_see_str} | Вызовы: Стр: {self.stats['Стрельба']}, Гр: {self.stats['Граната']}"
