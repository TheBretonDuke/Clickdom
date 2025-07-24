# File: main.py
import pygame
from config.settings import MENU_SIZE, GAME_SIZE, ASSETS_DIR, ASSETS, PALEWOOD
from ui.menu import show_menu, show_end_screen
from ui.game_solo import GameSolo
from ui.game_multi import GameMultiplayer

def init_window(size):
    return pygame.display.set_mode(size)

def show_connection_error(screen, font):
    screen = init_window(MENU_SIZE)
    try:
        img = pygame.image.load(str(ASSETS['connexion_bg'])).convert()
        background = pygame.transform.scale(img, MENU_SIZE)
    except FileNotFoundError:
        background = pygame.Surface(MENU_SIZE)
        background.fill(PALEWOOD)
    msg = "Connexion au serveur impossible."
    shadow = font.render(msg, True, (0,0,0))
    text   = font.render(msg, True, (255,255,255))
    rect   = text.get_rect(center=(MENU_SIZE[0]//2, MENU_SIZE[1]//2))
    background.blit(shadow, rect.move(2,2))
    background.blit(text, rect)
    screen.blit(background, (0,0))
    pygame.display.flip()
    pygame.time.wait(4000)

def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        print("🔇 Audio indisponible")
    pygame.display.set_caption("Clickdom")

    fp     = ASSETS_DIR / "PressStart2P-Regular.ttf"
    font   = pygame.font.Font(str(fp), 12)
    font_b = pygame.font.Font(str(fp), 20)
    screen = init_window(MENU_SIZE)

    while True:
        mode, n_bots = show_menu(screen, MENU_SIZE, font, font_b)

        if mode == 'solo':
            screen = init_window(GAME_SIZE)
            winner, final_grid = GameSolo(
                screen, GAME_SIZE, font, font_b,
                bot_count=n_bots
            ).run()
        else:
            screen = init_window(GAME_SIZE)
            try:
                winner, final_grid = GameMultiplayer(
                    screen, GAME_SIZE, font, font_b
                ).run()
            except Exception:
                show_connection_error(screen, font)
                continue

        # Calcul classements
        scores = {}
        for row in final_grid:
            for cell in row:
                pid = cell['owner']
                if pid>0:
                    scores.setdefault(pid,{'cells':0,'strength':0})
                    scores[pid]['cells']   +=1
                    scores[pid]['strength']+=cell['strength']
        rankings = sorted(scores.items(), key=lambda x: x[1]['strength'], reverse=True)

        screen = init_window(MENU_SIZE)
        show_end_screen(screen, MENU_SIZE, font_b, winner, rankings)

if __name__=='__main__':
    main()
