import socket
import threading
import json
from config import CONFIG_PARAMS

def handle_client(conn, workers):
    try:
        data = conn.recv(2048)
        if not data:
            return

        task = json.loads(data.decode('utf-8'))
        worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        worker_sock.connect(("127.0.0.1", workers[0]))

        worker_sock.sendall(data)
        result = worker_sock.recv(2048)
        conn.sendall(result)

        worker_sock.close()
    except Exception as e:
        print("Error manejando cliente:", e)
    finally:
        conn.close()

def server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", CONFIG_PARAMS['SERVER_PORT']))
    server_sock.listen(CONFIG_PARAMS['SERVER_MAX_CLIENTS'])
    print(f"Servidor activo en {CONFIG_PARAMS['SERVER_IP_ADDRESS']}:{CONFIG_PARAMS['SERVER_PORT']}...")

    workers = [8082, 8083]  # Puertos de los workers
    while True:
        conn, _ = server_sock.accept()
        threading.Thread(target=handle_client, args=(conn, workers)).start()

if __name__ == '__main__':
    server()