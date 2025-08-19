from network.client import send_click
import time

print("📤 Simulation de clics pour 4 joueurs...")

# Simulation de quelques clics pour 4 joueurs
actions = [
    (1, 5, 5),
    (2, 5, 6),
    (3, 5, 7),
    (4, 6, 5),
    (1, 5, 5),
    (2, 5, 6),
    (3, 6, 7),
    (4, 6, 6),
]

for player, row, col in actions:
    send_click(row, col, player_id=player)
    time.sleep(0.5)

print("\n✅ Test multijoueur terminé.")
