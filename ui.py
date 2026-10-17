import pygame
from config import COLOR_UI_ACTIVE, COLOR_UI_INACTIVE, COLOR_TEXT

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_active = False

    def draw(self, screen):
        # Определение цвета в зависимости от активности кнопки
        color = COLOR_UI_ACTIVE if self.is_active else COLOR_UI_INACTIVE
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, width=2, border_radius=5)
        
        # Рендеринг текста внутри кнопки
        text_surf = self.font.render(self.text, True, (255, 255, 255) if self.is_active else COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        """Возвращает True, если на кнопку кликнули мышкой."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
