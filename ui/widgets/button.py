import pygame
from config.settings import ASSETS, ASSETS_DIR

class Button:
    def __init__(self, text, pos, size=(350,70), font_size=32, text_color=(240,240,220)):
        self.rect = pygame.Rect(pos, size)
        # Image de fond
        try:
            img = pygame.image.load(str(ASSETS['button_bg']))
            self.bg = pygame.transform.scale(img, size)
        except FileNotFoundError:
            self.bg = pygame.Surface(size)
            self.bg.fill((100,100,100))
        # Texte
        FONT_PATH = ASSETS_DIR / "PressStart2P-Regular.ttf"
        self.font = pygame.font.Font(str(FONT_PATH), font_size)
        self.text = text
        self.color = text_color
        self.surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        screen.blit(self.bg, self.rect)
        screen.blit(self.surface, self.text_rect)

    def is_clicked(self, event):
        return event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(event.pos)