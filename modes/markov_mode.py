import pygame
import random
from config import (MARKOV_INTERVAL, MARKOV_MATRIX, NPC_SIZE,
                    COLOR_NPC, draw_triangle, SHELTER_RECT)

class MarkovMode:
    def __init__(self, player):
        self.player = player
        # Точка внутри укрытия и точка ведения огня рядом
        self.hiding_pos = pygame.Vector2(SHELTER_RECT.centerx, SHELTER_RECT.centery)
        self.firing_pos = pygame.Vector2(SHELTER_RECT.centerx, SHELTER_RECT.top - 40)
        
        self.npc_pos = pygame.Vector2(self.hiding_pos)
        self.npc_heading = pygame.Vector2(0, -1)
        
        self.state = "Укрытие"
        self.state_timer = 0.0
        self.stats = {"Стрельба": 0, "Граната": 0}
        
        self.flash_timer = 0.0
        self.current_color = COLOR_NPC

    def update(self, dt):
        self.state_timer += dt
        
        # Взгляд всегда на игрока
        desired = self.player.pos - self.npc_pos
        if desired.length_squared() > 0:
            self.npc_heading = desired.normalize()

        # Смена состояний по таймеру
        if self.state_timer >= MARKOV_INTERVAL:
            self.state_timer = 0.0
            self.transition_to_next_state()

        # Логика перемещения и мигания
        self.flash_timer += dt
        if self.state == "Укрытие":
            self.current_color = COLOR_NPC
            # ИИ плавно идет прятаться в укрытие
            move_dir = self.hiding_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 150 * dt
                
        elif self.state == "Стрельба":
            # ИИ выходит из укрытия, чтобы пострелять
            move_dir = self.firing_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 150 * dt
                
            if self.flash_timer >= 0.1:
                self.current_color = (255, 100, 100) if self.current_color == COLOR_NPC else COLOR_NPC
                self.flash_timer = 0.0
                
        elif self.state == "Граната":
            # ИИ делает выпад в сторону для броска
            move_dir = self.firing_pos - self.npc_pos
            if move_dir.length() > 2:
                self.npc_pos += move_dir.normalize() * 150 * dt
                
            if self.flash_timer >= 0.1:
                self.current_color = (241, 196, 15) if self.current_color == (230, 126, 34) else (230, 126, 34)
                self.flash_timer = 0.0

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
        # Рисуем зону укрытия полупрозрачной или просто зеленым контуром
        pygame.draw.rect(screen, (46, 204, 113), SHELTER_RECT, width=3, border_radius=4)
        
        # Рисуем NPC
        draw_triangle(screen, self.npc_pos, self.npc_heading, NPC_SIZE, self.current_color)
        
        # Эффекты атаки
        if self.state == "Стрельба":
            pygame.draw.line(screen, (255, 0, 0), self.npc_pos, self.player.pos, 2)
        elif self.state == "Граната":
            pygame.draw.circle(screen, (241, 196, 15), (int(self.player.pos.x), int(self.player.pos.y)), 60, width=2)

    def get_info_text(self):
        return f"Markov | Состояние: {self.state} | Вызовы: Стрельба: {self.stats['Стрельба']} | Граната: {self.stats['Граната']}"
