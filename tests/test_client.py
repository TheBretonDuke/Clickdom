# test_client.py

from network.client import send_click

print("📤 Envoi de 3 clics au serveur...\n")

send_click(12, 7)
send_click(12, 7)
send_click(13, 7)

print("\n✅ Test terminé.")
