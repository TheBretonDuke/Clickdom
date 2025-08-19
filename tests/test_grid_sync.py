from network.client import send_click
import time

def print_grid(grid):
    print("\n=== Grille actuelle ===")
    for row in grid:
        line = ""
        for cell in row:
            owner = cell["owner"]
            if owner == 0:
                line += ". "
            else:
                line += f"{owner} "
        print(line)
    print()

def test_sync():
    player_id = 1
    clicks = [(5, 5), (5, 6), (6, 5), (6, 6)]

    for (row, col) in clicks:
        print(f"🎯 Clic sur ({row}, {col}) par joueur {player_id}")
        grid = send_click(row, col, player_id)
        if grid:
            print_grid(grid)
        else:
            print("⚠️ Aucune grille reçue.")
        time.sleep(1)

if __name__ == "__main__":
    test_sync()
