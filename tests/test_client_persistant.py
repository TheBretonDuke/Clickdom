from network.client import ClickdomClient, afficher_grille

def test():
    client = ClickdomClient()
    try:
        for row, col in [(5, 5), (5, 6), (6, 5), (6, 6)]:
            print(f"🎯 Clic sur ({row}, {col})")
            grid = client.send_click(row, col)
            if grid:
                afficher_grille(grid)
        print("📡 Demande manuelle de la grille (GET_GRID)")
        grid = client.get_grid()
        if grid:
            afficher_grille(grid)
    finally:
        client.close()

if __name__ == "__main__":
    test()
