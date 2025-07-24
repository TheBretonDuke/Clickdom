import socket
import threading
import json
from pathlib import Path
from grid import create_empty_grid, click_case, capture_enclosed_zones

HOST, PORT = '127.0.0.1', None
# Choix aléatoire de port
import random
PORT = random.randint(6000,7000)
# Enregistrement du port
Path('current_port.txt').write_text(str(PORT))

# Grille et synchronisation
grid = create_empty_grid()
lock = threading.Lock()
next_id = 1


def handle_client(conn, addr):
    global next_id
    with lock:
        pid = next_id; next_id += 1
    conn.sendall(str(pid).encode())
    try:
        while True:
            data = conn.recv(1024)
            if not data: break
            msg = data.decode()
            with lock:
                if msg == 'GET_GRID':
                    resp = {'grid': grid}
                else:
                    try:
                        r,c = map(int,msg.split(','))
                        click_case(grid,pid,r,c)
                        capture_enclosed_zones(grid,pid)
                        resp = {'grid':grid}
                    except Exception as e:
                        resp = {'error':str(e),'grid':grid}
            conn.sendall(json.dumps(resp).encode())
    finally:
        conn.close()


def main():
    print(f"Server on {HOST}:{PORT}")
    srv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    srv.bind((HOST,PORT)); srv.listen()
    try:
        while True:
            conn,addr = srv.accept()
            threading.Thread(target=handle_client,args=(conn,addr),daemon=True).start()
    except KeyboardInterrupt:
        print("Stopping server")
    finally:
        srv.close()


if __name__=='__main__':
    main()