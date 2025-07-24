import random
from config.settings import GRID_SIZE


def create_empty_grid():
    return [[{'owner': 0, 'strength': 0} for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def is_adjacent_to_player(grid, row, col, player):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = row+dr, col+dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            if grid[nr][nc]['owner'] == player:
                return True
    return False


def click_case(grid, player, row, col):
    cell = grid[row][col]
    if cell['owner'] == 0 and is_adjacent_to_player(grid, row, col, player):
        cell.update(owner=player, strength=1)
    elif cell['owner'] == player:
        cell['strength'] += 1
    else:
        cell['strength'] -= 1
        if cell['strength'] <= 0:
            cell.update(owner=player, strength=1)


def capture_enclosed_zones(grid, player):
    visited = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]

    def flood(r, c):
        stack = [(r,c)]
        zone, border = [], False
        while stack:
            x, y = stack.pop()
            if visited[x][y]: continue
            visited[x][y] = True
            zone.append((x,y))
            if x in (0, GRID_SIZE-1) or y in (0, GRID_SIZE-1):
                border = True
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0<=nx<GRID_SIZE and 0<=ny<GRID_SIZE:
                    if not visited[nx][ny] and grid[nx][ny]['owner'] != player:
                        stack.append((nx,ny))
        return zone, border

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if not visited[r][c] and grid[r][c]['owner'] not in (player,0):
                zone, border = flood(r,c)
                if not border:
                    for x,y in zone:
                        grid[x][y].update(owner=player, strength=1)


def get_possible_moves(grid, player):
    moves = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c]['owner']==player:
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0<=nr<GRID_SIZE and 0<=nc<GRID_SIZE and grid[nr][nc]['owner']!=player:
                        moves.append((nr,nc))
    return moves


def check_victory(grid):
    players = {cell['owner'] for row in grid for cell in row if cell['owner']>0}
    return players if players else set()