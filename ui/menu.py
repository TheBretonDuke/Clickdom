import pygame
from config.settings import ASSETS, PALEWOOD
from ui.widgets.button import Button
from config.settings import PLAYER_COLORS_RGB


def select_bot_count(screen, window_size, font_big):
    """Affiche un écran de sélection du nombre de bots pour le mode solo."""
    clock = pygame.time.Clock()
    w, h = window_size
    # Fond
    background = pygame.Surface(window_size)
    background.fill(PALEWOOD)

    # Titre
    title = "Nombre de bots"
    text_title = font_big.render(title, True, (255, 255, 255))
    shadow_title = font_big.render(title, True, (0, 0, 0))
    rect_title = text_title.get_rect(center=(w//2, 100))
    background.blit(shadow_title, rect_title.move(2,2))
    background.blit(text_title, rect_title)

    # Boutons 1 à 7
    buttons = []
    btn_size = (60, 60)
    margin = 20
    total_width = 7 * btn_size[0] + (7 - 1) * margin
    start_x = (w - total_width) // 2
    y = h // 2
    for i in range(1, 8):
        x = start_x + (i - 1) * (btn_size[0] + margin)
        btn = Button(str(i), pos=(x, y), size=btn_size, font_size=30)
        btn.text_rect = btn.surface.get_rect(center=btn.rect.center)
        buttons.append((i, btn))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            for count, btn in buttons:
                if btn.is_clicked(event):
                    return count
        screen.blit(background, (0, 0))
        for _, btn in buttons:
            btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def show_menu(screen, window_size, font, font_big):
    """
    Affiche le menu principal et retourne :
      - ('solo', n_bots) si solo choisi
      - ('multi', None) si multi choisi
    """
    clock = pygame.time.Clock()
    w, h = window_size

    # Fond
    try:
        img = pygame.image.load(str(ASSETS['menu_bg'])).convert()
        background = pygame.transform.scale(img, window_size)
    except FileNotFoundError:
        background = pygame.Surface(window_size)
        background.fill(PALEWOOD)

    # Musique
    try:
        pygame.mixer.music.load(str(ASSETS['music_menu']))
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    # Boutons Solo et Multi
    btn_size = (350, 70)
    font_size = font_big.get_height()
    solo_btn = Button("Jouer en solo", pos=(0,0), size=btn_size, font_size=font_size)
    multi_btn = Button("Jouer en multi", pos=(0,0), size=btn_size, font_size=font_size)

    solo_btn.rect.center = (w//2, h//2 - 50)
    multi_btn.rect.center = (w//2, h//2 + 50)
    solo_btn.text_rect = solo_btn.surface.get_rect(center=solo_btn.rect.center)
    multi_btn.text_rect = multi_btn.surface.get_rect(center=multi_btn.rect.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if solo_btn.is_clicked(event):
                n_bots = select_bot_count(screen, window_size, font_big)
                return ('solo', n_bots)
            if multi_btn.is_clicked(event):
                return ('multi', None)

        screen.blit(background, (0, 0))
        solo_btn.draw(screen)
        multi_btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def show_end_screen(screen, window_size, font, winner, rankings=None):
    clock = pygame.time.Clock()
    w, h = window_size

    # Fond
    try:
        img = pygame.image.load(str(ASSETS['ending_bg'])).convert_alpha()
        background = pygame.transform.scale(img, window_size)
    except FileNotFoundError:
        background = pygame.Surface(window_size)
        background.fill(PALEWOOD)

    # Message
    if winner is not None:
        msg = f"Joueur {winner} a gagné !"
    else:
        msg = "Fin de la partie"
    shadow = font.render(msg, True, (0, 0, 0))
    text = font.render(msg, True, (255, 255, 255))
    title_rect = text.get_rect(center=(w//2, 80))
    background.blit(shadow, title_rect.move(2,2))
    background.blit(text, title_rect)

    # Classement
    if rankings:
        y_offset = 160
        for pid, data in rankings:
            label = f"J{pid}: {data['cells']} cases, {data['strength']} pts"
            sh = font.render(label, True, (0, 0, 0))
            background.blit(sh, (w//2 - sh.get_width()//2 + 2, y_offset + 2))
            col = PLAYER_COLORS_RGB.get(pid, (255,255,255))
            tx = font.render(label, True, col)
            background.blit(tx, (w//2 - tx.get_width()//2, y_offset))
            y_offset += font.get_height() + 10

    # Boutons
    btn_size = (200, 50)
    btn_font = font.get_height()
    replay_btn = Button("Rejouer", pos=(0,0), size=btn_size, font_size=btn_font)
    quit_btn = Button("Quitter", pos=(0,0), size=btn_size, font_size=btn_font)
    replay_btn.rect.center = (w//2, h - 120)
    quit_btn.rect.center   = (w//2, h - 50)
    replay_btn.text_rect = replay_btn.surface.get_rect(center=replay_btn.rect.center)
    quit_btn.text_rect = quit_btn.surface.get_rect(center=quit_btn.rect.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if replay_btn.is_clicked(event):
                return
            if quit_btn.is_clicked(event):
                pygame.quit()
                exit()

        screen.blit(background, (0,0))
        replay_btn.draw(screen)
        quit_btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)