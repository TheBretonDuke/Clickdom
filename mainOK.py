import pygame
import sys
import random

pygame.init()
pygame.mixer.init()  # Initialise le module audio

pygame.mixer.music.load("Kingdom of Clicks V2.mp3")  # ou "music.ogg"
pygame.mixer.music.play(-1)  # -1 = boucle infinie
pygame.mixer.music.set_volume(1)  # entre 0.0 et 1.0

font = pygame.font.SysFont("Herculanum", 24)

# Taille de la fenêtre
window_size = (800, 800)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Clickdom")

# Couleurs
palewood = (233, 222, 162) # Plateau
blue = (63, 101, 190) # Joueur 1
red = (190, 63, 63)  # Joueur 2
grey = (120, 120, 120) # Grille

grid_size = 20
cell_size = window_size[0] // grid_size  # 40 pixels

# Initialiser la grille : chaque case contient son propriétaire (0 = vide) et sa strength
grid = [[{'owner': 0, 'strength': 0} for _ in range(grid_size)] for _ in range(grid_size)]

# Case de départ joueur 1 (humain), aléatoire
start_row = random.randint(0, grid_size - 1)
start_col = random.randint(0, grid_size - 1)
grid[start_row][start_col] = {'owner': 1, 'strength': 1}

# Case de départ bot (joueur 2), assez éloignée du joueur 1
while True:
    bot_row = random.randint(0, grid_size - 1)
    bot_col = random.randint(0, grid_size - 1)
    if abs(bot_row - start_row) + abs(bot_col - start_col) > 5:
        grid[bot_row][bot_col] = {'owner': 2, 'strength': 1}
        break

# Menu titre
def show_menu():
    menu_running = True
    title_font = pygame.font.SysFont("Herculanum", 64)
    button_font = pygame.font.SysFont("Herculanum", 36)

    while menu_running:
        screen.fill(palewood)

        # Titre du jeu
        title_text = title_font.render("Clickdom", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(window_size[0]//2, 200))
        screen.blit(title_text, title_rect)

        # Bouton Jouer
        button_text = button_font.render("Jouer", True, (255, 255, 255))
        button_rect = pygame.Rect(window_size[0]//2 - 100, 400, 200, 60)
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

# Vérifie si une case est adjacente au joueur
def is_adjacent_to_player(row, col, player):
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if 0 <= nr < grid_size and 0 <= nc < grid_size:
            if grid[nr][nc]['owner'] == player:
                return True
    return False

# Clic d’un joueur sur une case
def click_case(player, row, col):
    case = grid[row][col]
    if case['owner'] == 0 and is_adjacent_to_player(row, col, player):
        case['owner'] = player
        case['strength'] = 1
    elif case['owner'] == player:
        case['strength'] += 1
    elif case['owner'] != 0:
        case['strength'] -= 1
        if case['strength'] <= 0:
            case['owner'] = player
            case['strength'] = 1

# Déplacements possibles (adjacents à ses cases)
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

# Encerclement : capture les zones fermées par les cases du joueur
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

        # Vérifie que tous les voisins sont ennemis (pas de vides)
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

# Tour du bot
def bot_move():
    moves = get_possible_moves(2)
    if moves:
        r, c = random.choice(moves)
        click_case(2, r, c)

# Timers
GROWTH_EVENT = pygame.USEREVENT + 1
BOT_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(GROWTH_EVENT, 10000)
pygame.time.set_timer(BOT_EVENT, 400)

# Lancer le menu d’accueil
show_menu()

# Boucle principale
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
            capture_enclosed_zones(2)

    # Affichage
    screen.fill(palewood)
    for row in range(grid_size):
        for col in range(grid_size):
            rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)

            if grid[row][col]['owner'] == 1:
                pygame.draw.rect(screen, blue, rect)
            elif grid[row][col]['owner'] == 2:
                pygame.draw.rect(screen, red, rect)
            else:
                pygame.draw.rect(screen, palewood, rect)

            # Afficher strength uniquement si case possédée
            if grid[row][col]['owner'] != 0:
                strength = str(grid[row][col]['strength'])
                text = font.render(strength, True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

            pygame.draw.rect(screen, grey, rect, 1)

    pygame.display.flip()

pygame.quit()
sys.exit()
