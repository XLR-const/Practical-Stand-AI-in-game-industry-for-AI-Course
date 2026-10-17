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

# Стены (во всех режимах)
WALL_VERTICAL = pygame.Rect(450, 200, 40, 400)    # Вертикальная стена
WALL_HORIZONTAL = pygame.Rect(650, 350, 350, 40)  # Горизонтальная стена
COLOR_WALL = (1, 16, 166)                     # Серый цвет стен

# Настройки Игрока
PLAYER_RADIUS = 15
PLAYER_SPEED = 200.0

# Настройки NPC
NPC_SIZE = 20

# Режим 1: FSM
FSM_SPEED_PATROL = 100.0
FSM_SPEED_CHASE = 180.0
FSM_SPEED_RETREAT = 220.0
FSM_DIST_CHASE = 300.0
FSM_DIST_ATTACK = 80.0
FSM_DIST_PATROL = 400.0
FSM_HEALTH_DECREASE_DIST = 80.0
FSM_HEALTH_DECREASE_RATE = 20.0
FSM_HEALTH_RECOVER_RATE = 15.0

# Режим 2: Flocking
FLOCK_COUNT = 30
FLOCK_MAX_SPEED = 180.0
FLOCK_MAX_FORCE = 5.0
FLOCK_SEPARATION_DIST = 35.0
FLOCK_NEIGHBOR_DIST = 100.0
FLOCK_WEIGHT_SEPARATION = 1.8
FLOCK_WEIGHT_ALIGNMENT = 1.0
FLOCK_WEIGHT_COHESION = 0.8

# Режим 3: Markov
MARKOV_INTERVAL = 2.0
MARKOV_MATRIX = {
    "Укрытие":  [0.0, 0.5, 0.5],
    "Стрельба": [0.0, 0.7, 0.3],
    "Граната":  [0.0, 0.3, 0.7]
}

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

def check_line_of_sight(pos1, pos2):
    """Возвращает True, если между pos1 и pos2 нет стен (прямая видимость)."""
    start = (int(pos1.x), int(pos1.y))
    end = (int(pos2.x), int(pos2.y))
    if WALL_VERTICAL.clipline(start, end) or WALL_HORIZONTAL.clipline(start, end):
        return False
    return True

def handle_wall_collision(old_pos, new_pos, radius=10):
    """Проверяет столкновение со всеми стенами и плавно скользит по ним."""
    res_pos = pygame.Vector2(new_pos)
    for wall in [WALL_VERTICAL, WALL_HORIZONTAL]:
        if wall.inflate(radius * 2, radius * 2).collidepoint(res_pos.x, res_pos.y):
            # Проверяем раздельно оси, обеспечивая плавное скольжение вдоль стен
            if not wall.inflate(radius * 2, radius * 2).collidepoint(new_pos.x, old_pos.y):
                res_pos = pygame.Vector2(new_pos.x, old_pos.y)
            elif not wall.inflate(radius * 2, radius * 2).collidepoint(old_pos.x, new_pos.y):
                res_pos = pygame.Vector2(old_pos.x, new_pos.y)
            else:
                res_pos = pygame.Vector2(old_pos)
    return res_pos
