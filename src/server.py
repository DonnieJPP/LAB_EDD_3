import socket
import threading
import json
from config import CONFIG_PARAMS

# Configuration Parameters
IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
PORT = CONFIG_PARAMS['SERVER_PORT']


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
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilización de la dirección
    server_sock.bind(('127.0.0.1', 8081))  # Dirección y puerto correctos
    server_sock.listen(1)

    print("Esperando conexiones...")
    conn, addr = server_sock.accept()
    print(f"Conexión establecida con {addr}")
    
    # Lógica de procesamiento posterior
    conn.close()
    server_sock.close()

if __name__ == '__main__':
    server()