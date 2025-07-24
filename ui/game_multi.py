import pygame
import random
from config.settings import (
    GRID_SIZE, SIDEBAR_WIDTH, FPS,
    ASSETS, PLAYER_COLORS_RGB,
    DARKGREEN, PALEWOOD, GAME_TRACKS
)
from engine.grid import capture_enclosed_zones, check_victory, is_adjacent_to_player
from network.client import ClientNetwork

class GameMultiplayer:
    def __init__(self, screen, window_size, font, font_big):
        self.screen = screen
        self.window_size = window_size
        self.font = font
        self.font_big = font_big

        self.game_width = window_size[0] - SIDEBAR_WIDTH
        self.cell_size = self.game_width // GRID_SIZE

        self.net = ClientNetwork()
        self.player_id = self.net.player_id

        try:
            img = pygame.image.load(str(ASSETS['board'])).convert()
            full_board = pygame.transform.scale(img, window_size)
        except FileNotFoundError:
            full_board = pygame.Surface(window_size)
            full_board.fill(PALEWOOD)
        self.full_board = full_board
        self.board_image = pygame.Surface((self.game_width, window_size[1]))
        self.board_image.blit(full_board, (0, 0),
                              pygame.Rect(0, 0, self.game_width, window_size[1]))

        self.current_track_index = random.randrange(len(GAME_TRACKS))
        try:
            pygame.mixer.music.load(GAME_TRACKS[self.current_track_index])
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        self.running = True
        self.winner = None
        self.start_time = pygame.time.get_ticks()  # Timer 3mn

    def update_music(self):
        if not pygame.mixer.music.get_busy():
            self.current_track_index = (self.current_track_index + 1) % len(GAME_TRACKS)
            try:
                pygame.mixer.music.load(GAME_TRACKS[self.current_track_index])
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    def run(self):
        clock = pygame.time.Clock()

        while True:
            # Fin auto après 3min
            if pygame.time.get_ticks() - self.start_time >= 180000:
                break

            grid = self.net.get_grid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.net.close()
                    return None, grid
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if x < self.game_width:
                        row = y // self.cell_size
                        col = x // self.cell_size
                        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                            if (grid[row][col]['owner'] == self.player_id or
                                is_adjacent_to_player(grid, row, col, self.player_id)):
                                grid = self.net.send_click(row, col)

            self.update_music()

            players = check_victory(grid)
            if players and len(players) == 1:
                self.winner = players.pop()
                break

            # Rendu grille
            self.screen.blit(self.board_image, (0, 0))
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    cell = grid[r][c]
                    rect = pygame.Rect(c*self.cell_size,
                                       r*self.cell_size,
                                       self.cell_size, self.cell_size)
                    owner = cell['owner']
                    if owner:
                        pygame.draw.rect(self.screen,
                                         PLAYER_COLORS_RGB[owner],
                                         rect)
                        txt = self.font.render(str(cell['strength']), True, (0,0,0))
                        self.screen.blit(txt, txt.get_rect(center=rect.center))
                    pygame.draw.rect(self.screen, DARKGREEN, rect, 1)

            # Sidebar & scores
            self.screen.blit(self.full_board,
                             pygame.Rect(self.game_width, 0,
                                         SIDEBAR_WIDTH, self.window_size[1]),
                             area=pygame.Rect(self.game_width, 0,
                                              SIDEBAR_WIDTH, self.window_size[1]))
            y = 20
            for pid in range(1, 9):
                cnt = sum(cell['owner']==pid for row in grid for cell in row)
                if cnt == 0: continue
                strt = sum(cell['strength'] for row in grid for cell in row if cell['owner']==pid)
                label = f"J{pid}: {cnt} cases, {strt} pts"
                sh = self.font.render(label, True, (0,0,0))
                tx = self.font.render(label, True, PLAYER_COLORS_RGB[pid])
                self.screen.blit(sh, (self.game_width+5, y+5))
                self.screen.blit(tx, (self.game_width+4, y+4))
                y += 30

            # Timer
            elapsed = pygame.time.get_ticks() - self.start_time
            remaining = max(0, 180000 - elapsed)
            m = remaining // 60000
            s = (remaining % 60000) // 1000
            tstr = f"{m:02d}:{s:02d}"
            shadow = self.font.render(tstr, True, (0,0,0))
            self.screen.blit(shadow, (self.game_width+7, y+7))
            txt = self.font.render(tstr, True, (255,255,255))
            self.screen.blit(txt, (self.game_width+5, y+5))

            pygame.display.flip()
            clock.tick(FPS)

        # Fin par timer ou victoire
        self.net.close()
        if self.winner is None:
            strengths = {
                pid: sum(cell['strength']
                         for row in grid for cell in row
                         if cell['owner']==pid)
                for pid in range(1, 9)
            }
            strengths = {pid: s for pid, s in strengths.items() if s>0}
            if strengths:
                self.winner = max(strengths, key=strengths.get)
        return self.winner, grid