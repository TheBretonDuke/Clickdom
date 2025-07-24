# File: ui/game_solo.py
import pygame
import random
import math
from config.settings import (
    GRID_SIZE, SIDEBAR_WIDTH, FPS,
    ASSETS, PLAYER_COLORS_RGB,
    DARKGREEN, PALEWOOD, GAME_TRACKS
)
from engine.grid import (
    create_empty_grid,
    click_case,
    capture_enclosed_zones,
    get_possible_moves,
    check_victory,
    is_adjacent_to_player
)

class GameSolo:
    def __init__(self, screen, window_size, font, font_big, bot_count=6):
        self.screen      = screen
        self.window_size = window_size
        self.font        = font
        self.font_big    = font_big

        # Zone de jeu
        self.game_width = window_size[0] - SIDEBAR_WIDTH
        self.cell_size  = self.game_width // GRID_SIZE

        # Chargement du plateau
        try:
            img = pygame.image.load(str(ASSETS['board'])).convert()
            full_board = pygame.transform.scale(img, window_size)
        except FileNotFoundError:
            full_board = pygame.Surface(window_size)
            full_board.fill(PALEWOOD)
        self.full_board  = full_board
        self.board_image = pygame.Surface((self.game_width, window_size[1]))
        self.board_image.blit(
            full_board, (0, 0),
            pygame.Rect(0, 0, self.game_width, window_size[1])
        )

        # Grille & joueurs
        self.grid      = create_empty_grid()
        self.player_id = 1
        self.bot_ids   = list(range(2, 2 + bot_count))

        # Timers
        self.GROWTH_EVENT = pygame.USEREVENT + 1
        self.BOT_EVENT    = pygame.USEREVENT + 2
        pygame.time.set_timer(self.GROWTH_EVENT, 10000)
        pygame.time.set_timer(self.BOT_EVENT,     500)  # toutes les 0,5 s

        # Timer 3 min
        self.start_time = pygame.time.get_ticks()

        self._init_positions()

        # Musique
        self.current_track_index = random.randrange(len(GAME_TRACKS))
        try:
            pygame.mixer.music.load(GAME_TRACKS[self.current_track_index])
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def _init_positions(self):
        """Place joueur et bots à distance >=5."""
        self.grid = create_empty_grid()
        r, c = random.randrange(GRID_SIZE), random.randrange(GRID_SIZE)
        self.grid[r][c] = {'owner': self.player_id, 'strength': 1}
        occupied = {(r, c)}
        for bot_id in self.bot_ids:
            while True:
                br, bc = random.randrange(GRID_SIZE), random.randrange(GRID_SIZE)
                if (br, bc) not in occupied and abs(br - r) + abs(bc - c) > 5:
                    self.grid[br][bc] = {'owner': bot_id, 'strength': 1}
                    occupied.add((br, bc))
                    break

    def update_music(self):
        if not pygame.mixer.music.get_busy():
            self.current_track_index = (self.current_track_index + 1) % len(GAME_TRACKS)
            try:
                pygame.mixer.music.load(GAME_TRACKS[self.current_track_index])
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    def _fast_strength(self, bot_id, move):
        """Heuristique rapide pour pré-filtrer les coups."""
        r, c = move
        cell = self.grid[r][c]
        return cell['strength'] + (cell['owner'] == 0)

    def _choose_move(self, bot_id):
        """
        IA hâtive : 
        1) Préfiltres top-3 moves par strength immédiate.
        2) Simule horizon-1 + heuristique territoriale sur ces candidats.
        """
        moves = get_possible_moves(self.grid, bot_id)
        if not moves:
            return None

        # 1) trier et ne garder que les 3 meilleurs moves par _fast_strength
        moves.sort(key=lambda mv: self._fast_strength(bot_id, mv), reverse=True)
        candidates = moves[:3]

        best_move, best_val = None, -math.inf
        for rr, cc in candidates:
            # simuler coup
            snapshot = self.grid[rr][cc].copy()
            owner_before = self.grid[rr][cc]['owner']
            click_case(self.grid, bot_id, rr, cc)
            capture_enclosed_zones(self.grid, bot_id)

            # évaluer score direct
            direct_score = sum(cell['strength']
                               for row in self.grid for cell in row
                               if cell['owner'] == bot_id)

            # heuristique territoriale simple (nombre de cases neutres et ennemies adjacentes)
            adj_count = sum(
                1
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]
                if 0 <= rr+dr < GRID_SIZE and 0 <= cc+dc < GRID_SIZE
                and self.grid[rr+dr][cc+dc]['owner'] != bot_id
            )
            val = direct_score + 0.3 * adj_count

            # horizon-1 adversaire (on simule un coup aléatoire du joueur)
            opp_moves = get_possible_moves(self.grid, self.player_id)
            if opp_moves:
                orr, occ = random.choice(opp_moves)
                opp_snapshot = self.grid[orr][occ].copy()
                click_case(self.grid, self.player_id, orr, occ)
                capture_enclosed_zones(self.grid, self.player_id)
                opp_score = sum(cell['strength']
                                for row in self.grid for cell in row
                                if cell['owner'] == self.player_id)
                val -= 0.2 * opp_score
                # restore opponent cell
                self.grid[orr][occ]['owner'] = opp_snapshot['owner']
                self.grid[orr][occ]['strength'] = opp_snapshot['strength']

            # restore our move
            self.grid[rr][cc]['owner'] = owner_before
            self.grid[rr][cc]['strength'] = snapshot['strength']

            if val > best_val:
                best_val, best_move = val, (rr, cc)

        return best_move or random.choice(moves)

    def run(self):
        clock = pygame.time.Clock()
        winner = None

        while True:
            # fin automatique après 3 minutes
            if pygame.time.get_ticks() - self.start_time >= 180_000:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, self.grid
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if x < self.game_width:
                        r = y // self.cell_size
                        c = x // self.cell_size
                        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                            if (self.grid[r][c]['owner'] == self.player_id or
                                is_adjacent_to_player(self.grid, r, c, self.player_id)):
                                click_case(self.grid, self.player_id, r, c)
                                capture_enclosed_zones(self.grid, self.player_id)
                elif event.type == self.GROWTH_EVENT:
                    for rr in range(GRID_SIZE):
                        for cc in range(GRID_SIZE):
                            if self.grid[rr][cc]['owner'] in ([self.player_id] + self.bot_ids):
                                self.grid[rr][cc]['strength'] += 1
                elif event.type == self.BOT_EVENT:
                    for bot_id in self.bot_ids:
                        move = self._choose_move(bot_id)
                        if move:
                            click_case(self.grid, bot_id, *move)
                            capture_enclosed_zones(self.grid, bot_id)

            self.update_music()

            players = check_victory(self.grid)
            if players and len(players) == 1:
                winner = players.pop()
                break

            # rendu + HUD
            self.screen.blit(self.board_image, (0, 0))
            self._draw_grid()
            sidebar = pygame.Rect(self.game_width, 0, SIDEBAR_WIDTH, self.window_size[1])
            self.screen.blit(self.full_board, sidebar, area=sidebar)
            self._draw_hud()
            pygame.display.flip()
            clock.tick(FPS)

        # détermination du gagnant si timer expiré
        if winner is None:
            strengths = {
                pid: sum(cell['strength']
                         for row in self.grid for cell in row
                         if cell['owner'] == pid)
                for pid in [self.player_id] + self.bot_ids
            }
            winner = max(strengths, key=strengths.get)

        return winner, self.grid

    def _draw_grid(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect  = pygame.Rect(c * self.cell_size, r * self.cell_size,
                                     self.cell_size, self.cell_size)
                owner = self.grid[r][c]['owner']
                if owner:
                    pygame.draw.rect(self.screen, PLAYER_COLORS_RGB[owner], rect)
                    txt = self.font.render(
                        str(self.grid[r][c]['strength']), True, (0, 0, 0)
                    )
                    self.screen.blit(txt, txt.get_rect(center=rect.center))
                pygame.draw.rect(self.screen, DARKGREEN, rect, 1)

    def _draw_hud(self):
        y = 20
        # Scores
        for pid in [self.player_id] + self.bot_ids:
            cnt  = sum(cell['owner'] == pid for row in self.grid for cell in row)
            strg = sum(cell['strength'] for row in self.grid for cell in row if cell['owner'] == pid)
            label = f"J{pid}: {cnt} c, {strg} pts"
            sh = self.font.render(label, True, (0, 0, 0))
            tx = self.font.render(label, True, PLAYER_COLORS_RGB[pid])
            self.screen.blit(sh, (self.game_width + 5, y + 5))
            self.screen.blit(tx, (self.game_width + 4, y + 4))
            y += 30

        # Timer restant
        elapsed   = pygame.time.get_ticks() - self.start_time
        remaining = max(0, 180_000 - elapsed)
        m         = remaining // 60000
        s         = (remaining % 60000) // 1000
        ts        = f"{m:02d}:{s:02d}"
        shadow    = self.font.render(ts, True, (0, 0, 0))
        self.screen.blit(shadow, (self.game_width + 7, y + 7))
        txt       = self.font.render(ts, True, (255, 255, 255))
        self.screen.blit(txt, (self.game_width + 5, y + 5))
