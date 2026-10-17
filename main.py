import pygame
import sys
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_TEXT, COLOR_PLAYER
from entities import Player
from ui import Button
from modes.fsm_mode import FSMMode
from modes.flocking_mode import FlockingMode
from modes.markov_mode import MarkovMode

class SimulationApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Учебный стенд игрового ИИ")
        self.clock = pygame.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("Arial", 22)
        self.font_ui = pygame.font.SysFont("Arial", 18)

        # Детерминированный спавн игрока
        self.player = Player(150, 450)

        # Инициализация кнопок управления
        self.buttons = {
            "FSM": Button(300, 15, 150, 50, "FSM", self.font_main),
            "Flocking": Button(500, 15, 150, 50, "Flocking", self.font_main),
            "Markov": Button(700, 15, 150, 50, "Markov", self.font_main)
        }

        # Выбор начального режима
        self.current_mode_name = "FSM"
        self.buttons[self.current_mode_name].is_active = True
        self.current_mode = FSMMode(self.player)

    def switch_mode(self, mode_name):
        """Сброс и инициализация выбранного режима симуляции."""
        self.current_mode_name = mode_name
        
        # Сброс подсветки кнопок
        for name, btn in self.buttons.items():
            btn.is_active = (name == mode_name)
            
        # Детерминированный сброс позиции игрока при перезапуске
        self.player.pos = pygame.Vector2(150, 450)
        
        # Перезапуск классов режимов
        if mode_name == "FSM":
            self.current_mode = FSMMode(self.player)
        elif mode_name == "Flocking":
            self.current_mode = FlockingMode(self.player)
        elif mode_name == "Markov":
            random.seed(42) # Фиксируем seed для Markov
            self.current_mode = MarkovMode(self.player)

    def run(self):
        running = True
        while running:
            # Ограничение FPS и получение дельты времени (в секундах)
            dt = self.clock.tick(FPS) / 1000.0

            # --- Обработка событий ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Горячие клавиши переключения режимов цифровым блоком
                    elif event.key == pygame.K_1: self.switch_mode("FSM")
                    elif event.key == pygame.K_2: self.switch_mode("Flocking")
                    elif event.key == pygame.K_3: self.switch_mode("Markov")
                
                # Обработка кликов по кнопкам мыши
                for name, btn in self.buttons.items():
                    if btn.handle_event(event):
                        self.switch_mode(name)

            # --- Обновление логики объектов ---
            self.player.update(dt)
            self.current_mode.update(dt)

            # --- Отрисовка кадра ---
            self.screen.fill(COLOR_BG)
            
            # Разделительная линия между UI панелью и симуляцией
            pygame.draw.line(self.screen, (70, 70, 70), (0, 80), (SCREEN_WIDTH, 80), 2)

            # Отрисовка игровых сущностей
            self.player.draw(self.screen, COLOR_PLAYER)
            self.current_mode.draw(self.screen)

            # Отрисовка интерфейса (Кнопки)
            for btn in self.buttons.values():
                btn.draw(self.screen)

            # Вывод информационного текста состояния ИИ
            info_text = self.current_mode.get_info_text()
            info_surf = self.font_main.render(info_text, True, COLOR_TEXT)
            self.screen.blit(info_surf, (20, 95))

            # Вывод подсказки по управлению внизу экрана
            help_text = "WASD / Стрелки — движение | Клавиши 1, 2, 3 — смена режимов | ESC — выход"
            help_surf = self.font_ui.render(help_text, True, (150, 150, 150))
            self.screen.blit(help_surf, (20, SCREEN_HEIGHT - 35))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = SimulationApp()
    app.run()
