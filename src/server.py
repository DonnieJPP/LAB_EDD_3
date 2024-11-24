import socket
import threading
import json
from config import CONFIG_PARAMS

IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
PORT = CONFIG_PARAMS['SERVER_PORT']
MAX_WORKERS = CONFIG_PARAMS['SERVER_MAX_WORKERS']

workers = []  # Lista para registrar las conexiones de workers

def handle_worker(conn, addr, worker_id):
    """
    Maneja la comunicación con un worker específico.
    """
    print(f"[Servidor] Worker {worker_id} conectado desde {addr}")
    try:
        while True:
            task = input(f"[Servidor] Ingresa la tarea para el Worker {worker_id} (o 'exit' para finalizar): ")
            if task.lower() == CONFIG_PARAMS['EXIT_MESSAGE']:
                print(f"[Servidor] Finalizando conexión con Worker {worker_id}")
                conn.sendall(CONFIG_PARAMS['EXIT_MESSAGE'].encode('utf-8'))
                break

            # Esperar respuesta del worker
            result = conn.recv(4096)
            if not result:
                print(f"[Servidor] Worker {worker_id} desconectado.")
                break
            print(f"[Servidor] Resultado del Worker {worker_id}: {result.decode('utf-8')}")
    except Exception as e:
        print(f"[Servidor] Error con Worker {worker_id}: {e}")
    finally:
        conn.close()

def start_server():
    """
    Inicia el servidor y espera conexiones de los workers.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP_ADDRESS, PORT))
    server.listen(MAX_WORKERS)
    print(f"[Servidor] Esperando hasta {MAX_WORKERS} workers en {IP_ADDRESS}:{PORT}...")

    worker_id = 0
    while len(workers) < MAX_WORKERS:
        conn, addr = server.accept()
        workers.append(conn)
        threading.Thread(target=handle_worker, args=(conn, addr, worker_id)).start()
        worker_id += 1

if __name__ == '__main__':
    start_server()
