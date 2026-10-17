import pygame
import math

# Настройки окна
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Цвета (RGB)
COLOR_BG = (30, 30, 30)
COLOR_TEXT = (220, 220, 220)
COLOR_PLAYER = (0, 150, 255)
COLOR_NPC = (255, 50, 50)
COLOR_UI_BG = (50, 50, 50)
COLOR_UI_ACTIVE = (46, 204, 113)
COLOR_UI_INACTIVE = (127, 140, 141)

# Настройки Игрока
PLAYER_RADIUS = 15
PLAYER_SPEED = 200.0

# Настройки препятствий и укрытий
WALL_RECT = pygame.Rect(350, 200, 40, 400)      # Вертикальная стена для FSM
SHELTER_RECT = pygame.Rect(580, 480, 50, 50)   # Квадратное укрытие для Markov
COLOR_WALL = (149, 165, 166)                   # Серый цвет для стен


# Настройки NPC (базовые)
NPC_SIZE = 20

# Режим 1: FSM
FSM_SPEED_PATROL = 100.0
FSM_SPEED_CHASE = 180.0
FSM_SPEED_RETREAT = 220.0
FSM_DIST_CHASE = 300.0
FSM_DIST_ATTACK = 80.0
FSM_DIST_PATROL = 400.0
FSM_HEALTH_DECREASE_DIST = 80.0
FSM_HEALTH_DECREASE_RATE = 20.0  # единиц здоровья в секунду
FSM_HEALTH_RECOVER_RATE = 15.0

# Режим 2: Flocking
FLOCK_COUNT = 30
FLOCK_MAX_SPEED = 200.0
FLOCK_MAX_FORCE = 4.0
FLOCK_SEPARATION_DIST = 40.0
FLOCK_NEIGHBOR_DIST = 100.0
FLOCK_WEIGHT_SEPARATION = 1.5
FLOCK_WEIGHT_ALIGNMENT = 1.0
FLOCK_WEIGHT_COHESION = 0.8

# Режим 3: Markov
MARKOV_INTERVAL = 2.0  # Смена состояния каждые 2 секунды
# Матрицы переходов: [В укрытие, Стрельба, Граната]
MARKOV_MATRIX = {
    "Укрытие":  [0.0, 0.5, 0.5],
    "Стрельба": [0.0, 0.7, 0.3],
    "Граната":  [0.0, 0.3, 0.7]
}

# Вспомогательная функция для отрисовки треугольника по направлению движения
def draw_triangle(screen, center, heading, size, color):
    """Отрисовка треугольника, повернутого по вектору направления."""
    if heading.length_squared() > 0:
        angle = math.atan2(heading.y, heading.x)
    else:
        angle = 0
        
    p1 = center + pygame.Vector2(math.cos(angle), math.sin(angle)) * size
    p2 = center + pygame.Vector2(math.cos(angle + 2.5), math.sin(angle + 2.5)) * (size * 0.6)
    p3 = center + pygame.Vector2(math.cos(angle - 2.5), math.sin(angle - 2.5)) * (size * 0.6)
    
    pygame.draw.polygon(screen, color, [p1, p2, p3])
