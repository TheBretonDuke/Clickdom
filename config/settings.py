from pathlib import Path
import pygame

# === DÉFINITIONS DE CHEMINS ===
# Répertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent
# Répertoire des assets (images, sons, polices)
ASSETS_DIR = BASE_DIR / "assets"

# === COULEURS GÉNÉRALES ===
PALEWOOD  = (233, 222, 162)
BLUE      = (30,  75,  179)
RED       = (169, 29,  29)
DARKGREEN = (67,  89,  66)

# === COULEURS JOUEURS ===
PLAYER_COLORS_RGB = {
    1: (30,  75,  179),  # 🔵 Bleu
    2: (29,  179, 29),   # 🟢 Vert
    3: (179, 29,  29),   # 🔴 Rouge
    4: (128, 0,   128),  # 🟣 Violet
    5: (255, 215, 0),    # 🟡 Jaune
    6: (255, 140, 0),    # 🟠 Orange
    7: (139, 69,  19),   # 🟤 Marron
    8: (49, 187, 180)     # Cyan
}

# === PARAMÈTRES DE JEU ===
GRID_SIZE     = 20           # Nombre de cases par ligne/colonne
FPS           = 60           # Framerate
SIDEBAR_WIDTH = 250          # Largeur de la barre latérale
MENU_SIZE     = (900, 900)   # Dimensions de la fenêtre menu
GAME_SIZE     = (MENU_SIZE[0] + SIDEBAR_WIDTH, MENU_SIZE[1])  # Dimensions de la fenêtre de jeu

# === CHEMINS VERS LES ASSETS ===
ASSETS = {
    "menu_bg":       str(ASSETS_DIR / "Clickdom_Main_V2.png"),
    "button_bg":     str(ASSETS_DIR / "button_bg.png"),
    "board":         str(ASSETS_DIR / "Board1.png"),
    "music_menu":    str(ASSETS_DIR / "Clickdom_Main_Title.mp3"),
    "ending_bg":     str(ASSETS_DIR / "Ending.png"),
    "connexion_bg":  str(ASSETS_DIR / "Connexion.png")
}

# === MUSIQUES DE FOND ===
GAME_TRACKS = [
    str(ASSETS_DIR / "Kingdom_of_Clicks_V2.mp3"),
    str(ASSETS_DIR / "Kingdom_of_Clicks.mp3"),
    str(ASSETS_DIR / "Clickdom.mp3")
]