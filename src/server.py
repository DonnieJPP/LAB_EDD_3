import socket
import threading
import json
from config import CONFIG_PARAMS

def handle_client(conn):
    try:
        buffer = b""
        while True:
            part = conn.recv(4096)
            if not part:
                break
            buffer += part
        task = json.loads(buffer.decode('utf-8'))
        print("[Servidor] Recibió tarea del cliente.")

        worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        worker_sock.connect((CONFIG_PARAMS['WORKER_0_IP'], CONFIG_PARAMS['WORKER_0_PORT']))
        worker_sock.sendall(json.dumps(task).encode('utf-8'))

        result = b""
        while True:
            part = worker_sock.recv(4096)
            if not part:
                break
            result += part
        conn.sendall(result)
        worker_sock.close()
        print("[Servidor] Resultado enviado al cliente.")
    except Exception as e:
        print("[Servidor] Error:", e)
    finally:
        conn.close()

def server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['SERVER_PORT']))
    server_sock.listen(5)
    print("[Servidor] Esperando conexiones...")
    while True:
        conn, addr = server_sock.accept()
        print(f"[Servidor] Conexión establecida con {addr}")
        threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == '__main__':
    server()
