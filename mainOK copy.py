import pygame
import sys
import random

# === MUSIQUES ===
GAME_TRACKS = [
    "Kingdom of Clicks V2.mp3",
    "Kingdom of Clicks.mp3",
    "Clickdom.mp3"
]

# === INITIALISATION ===
pygame.init()
pygame.mixer.init()
font = pygame.font.SysFont("Herculanum", 24)

# === FENETRE ===
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h
window_size = (min(900, screen_width), min(900, screen_height))
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Clickdom")

# === COULEURS ===
palewood = (233, 222, 162)
blue = (30, 75, 179)
red = (169, 29, 29)
darkgreen = (67, 89, 66, 0.20)

grid_size = 20 
cell_size = min(window_size[0], window_size[1]) // grid_size

# === GRILLE ===
grid = [[{'owner': 0, 'strength': 0} for _ in range(grid_size)] for _ in range(grid_size)]

# === MENU TITRE ===
def show_menu():
    menu_running = True
    title_font = pygame.font.SysFont("Herculanum", 64)
    button_font = pygame.font.SysFont("Herculanum", 36)

    # Charger et redimensionner l'image du menu
    bg_image = pygame.image.load("Clickdom Main V2.png").convert()
    bg_image = pygame.transform.scale(bg_image, window_size)

    pygame.mixer.music.load("Clickdom Main Title.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(1)

    while menu_running:
        screen.blit(bg_image, (0, 0))  # Afficher l’image en fond

        # Bouton
        button_text = button_font.render("Jouer", True, (255, 255, 255))
        button_rect = pygame.Rect(window_size[0] // 2 - 100, 650, 200, 60)
        pygame.draw.rect(screen, blue, button_rect, border_radius=10)
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    menu_running = False

        pygame.display.flip()

    pygame.mixer.music.stop()

# === MENU ===
show_menu()

# === MUSIQUE DE JEU ===
current_track_index = random.randint(0, len(GAME_TRACKS) - 1)
pygame.mixer.music.load(GAME_TRACKS[current_track_index])
pygame.mixer.music.play()
pygame.mixer.music.set_volume(1)

# === INITIALISATION DU JEU ===
start_row = random.randint(0, grid_size - 1)
start_col = random.randint(0, grid_size - 1)
grid[start_row][start_col] = {'owner': 1, 'strength': 1}

while True:
    bot_row = random.randint(0, grid_size - 1)
    bot_col = random.randint(0, grid_size - 1)
    if abs(bot_row - start_row) + abs(bot_col - start_col) > 5 and grid[bot_row][bot_col]['owner'] == 0:
        grid[bot_row][bot_col] = {'owner': 2, 'strength': 1}
        break

# === FONCTIONS ===
def is_adjacent_to_player(row, col, player):
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < grid_size and 0 <= nc < grid_size:
            if grid[nr][nc]['owner'] == player:
                return True
    return False

def click_case(player, row, col):
    case = grid[row][col]
    if case['owner'] == 0 and is_adjacent_to_player(row, col, player):
        case['owner'] = player
        case['strength'] = 1
    elif case['owner'] == player:
        case['strength'] += 1
    else:
        case['strength'] -= 1
        if case['strength'] <= 0:
            case['owner'] = player
            case['strength'] = 1

def get_possible_moves(player):
    moves = []
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c]['owner'] == player:
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < grid_size and 0 <= nc < grid_size:
                        if grid[nr][nc]['owner'] != player:
                            moves.append((nr, nc))
    return moves

def capture_enclosed_zones(player):
    visited = [[False for _ in range(grid_size)] for _ in range(grid_size)]

    def is_enclosed_area(r, c):
        to_check = [(r, c)]
        zone = []
        touches_border = False
        surrounded_by_enemy = True

        while to_check:
            x, y = to_check.pop()
            if visited[x][y]:
                continue
            visited[x][y] = True
            zone.append((x, y))

            if x == 0 or x == grid_size - 1 or y == 0 or y == grid_size - 1:
                touches_border = True

            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    if not visited[nx][ny]:
                        neighbor = grid[nx][ny]
                        if neighbor['owner'] != player:
                            to_check.append((nx, ny))
                else:
                    touches_border = True

        for x, y in zone:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    if grid[nx][ny]['owner'] == 0:
                        surrounded_by_enemy = False

        return (not touches_border and surrounded_by_enemy, zone)

    for r in range(grid_size):
        for c in range(grid_size):
            if not visited[r][c] and grid[r][c]['owner'] not in [player, 0]:
                enclosed, zone = is_enclosed_area(r, c)
                if enclosed:
                    for x, y in zone:
                        grid[x][y]['owner'] = player
                        grid[x][y]['strength'] = 1

def bot_move():
    moves = get_possible_moves(2)
    if moves:
        r, c = random.choice(moves)
        click_case(2, r, c)
        capture_enclosed_zones(2)

# === TIMERS ===
GROWTH_EVENT = pygame.USEREVENT + 1
BOT_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(GROWTH_EVENT, 10000)
pygame.time.set_timer(BOT_EVENT, 400)

# --- Plateau ---
board_image = pygame.image.load("Board 1.png")  # nom de l'image
board_image = pygame.transform.scale(board_image, window_size)

# === BOUCLE PRINCIPALE ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            col = x // cell_size
            row = y // cell_size
            if grid[row][col]['owner'] == 1 or is_adjacent_to_player(row, col, 1):
                click_case(1, row, col)
                capture_enclosed_zones(1)

        elif event.type == GROWTH_EVENT:
            for r in range(grid_size):
                for c in range(grid_size):
                    if grid[r][c]['owner'] in [1, 2]:
                        grid[r][c]['strength'] += 1

        elif event.type == BOT_EVENT:
            bot_move()

    # Si la musique s'est arrêtée, passer à la suivante
    if not pygame.mixer.music.get_busy():
        current_track_index = (current_track_index + 1) % len(GAME_TRACKS)
        pygame.mixer.music.load(GAME_TRACKS[current_track_index])
        pygame.mixer.music.play()

    # === AFFICHAGE ===
    screen.blit(board_image, (0, 0))
    for row in range(grid_size):
        for col in range(grid_size):
            rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)

            if grid[row][col]['owner'] == 1:
                pygame.draw.rect(screen, blue, rect)
            elif grid[row][col]['owner'] == 2:
                pygame.draw.rect(screen, red, rect)
            # sinon, ne rien dessiner pour laisser apparaître le fond


            if grid[row][col]['owner'] != 0:
                strength = str(grid[row][col]['strength'])
                text = font.render(strength, True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

            pygame.draw.rect(screen, darkgreen, rect, 1)

    pygame.display.flip()

pygame.quit()
sys.exit()