import socket
import json
from pathlib import Path

class ClientNetwork:
    def __init__(self):
        port_file = Path('current_port.txt')
        if not port_file.exists():
            raise FileNotFoundError("Lance d'abord le serveur")
        port = int(port_file.read_text())
        self.addr = ('127.0.0.1', port)
        self.sock = socket.socket()
        self.sock.connect(self.addr)
        self.player_id = int(self.sock.recv(1024).decode())
        print(f"Connected as J{self.player_id}")

    def get_grid(self):
        self.sock.sendall(b'GET_GRID')
        data = self.sock.recv(8192)
        return json.loads(data.decode())['grid']

    def send_click(self, r, c):
        msg = f"{r},{c}".encode()
        self.sock.sendall(msg)
        data = self.sock.recv(8192)
        return json.loads(data.decode()).get('grid', [])

    def close(self):
        self.sock.close()