import socket
import threading
import json
from config import CONFIG_PARAMS

class Server:
    def _init_(self):
        self.host = CONFIG_PARAMS['SERVER_IP_ADDRESS']
        self.port = CONFIG_PARAMS['SERVER_PORT']
        self.workers = {}  # Almacena las conexiones de los workers
        self.client = None
        self.client_lock = threading.Lock()
        self.server_socket = None
        self.total_time = 0
        print("[Servidor] Iniciando servidor...")

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"[Servidor] Servidor iniciado exitosamente en {self.host}:{self.port}")
            print("[Servidor] Esperando conexiones...")
            
            while True:
                conn, addr = self.server_socket.accept()
                # Esperar identificación
                id_msg = conn.recv(1024).decode()
                
                if id_msg.startswith('worker'):
                    worker_id = int(id_msg.split('_')[1])
                    self.workers[worker_id] = conn
                    print(f"[Servidor] Worker {worker_id} conectado desde {addr}")
                    print(f"[Servidor] Workers activos: {list(self.workers.keys())}")
                    threading.Thread(target=self.handle_worker, args=(worker_id, conn)).start()
                elif id_msg == 'client':
                    self.client = conn
                    print(f"[Servidor] Cliente conectado desde {addr}")
                    threading.Thread(target=self.handle_client, args=(conn,)).start()

        except Exception as e:
            print(f"[Servidor] Error al iniciar el servidor: {e}")

    def handle_worker(self, worker_id, conn):
        print(f"[Servidor] Iniciando manejo de Worker {worker_id}")
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    print(f"[Servidor] Conexión perdida con Worker {worker_id}")
                    break

                result = json.loads(data.decode())
                
                if 'status' in result and result['status'] == 'incomplete':
                    print(f"[Servidor] Worker {worker_id} no completó la tarea en tiempo")
                    print(f"[Servidor] Tiempo usado por Worker {worker_id}: {result['time_used']:.2f}s")
                    self.total_time += result['time_used']
                    
                    # Determinar el siguiente worker
                    next_worker_id = 1 if worker_id == 0 else 0
                    print(f"[Servidor] Intentando transferir tarea a Worker {next_worker_id}")
                    
                    if next_worker_id in self.workers:
                        next_task = {
                            'vector': result['partial_vector'],
                            'algorithm': result['algorithm'],
                            'time_limit': result['remaining_time'],
                            'total_time': self.total_time,
                            'progress': result.get('progress', 0)
                        }
                        print(f"[Servidor] Enviando tarea a Worker {next_worker_id}")
                        print(f"[Servidor] Progreso actual: {result.get('progress', 0):.2f}%")
                        self.workers[next_worker_id].send(json.dumps(next_task).encode())
                    else:
                        print(f"[Servidor] Worker {next_worker_id} no está disponible")
                    
                elif 'status' in result and result['status'] == 'complete':
                    print(f"[Servidor] Worker {worker_id} completó la tarea")
                    print(f"[Servidor] Tiempo total de ordenamiento: {result['time_used']:.2f}s")
                    if self.client:
                        print("[Servidor] Enviando resultado final al cliente")
                        self.client.send(json.dumps(result).encode())
                    else:
                        print("[Servidor] Cliente no disponible para recibir resultado")
                
            except Exception as e:
                print(f"[Servidor] Error con Worker {worker_id}: {e}")
                break
                
        print(f"[Servidor] Worker {worker_id} desconectado")
        if worker_id in self.workers:
            del self.workers[worker_id]
        conn.close()

    def handle_client(self, conn):
        print("[Servidor] Iniciando manejo de cliente")
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    print("[Servidor] Conexión perdida con el cliente")
                    break

                task = json.loads(data.decode())
                if task.get('command') == CONFIG_PARAMS['EXIT_MESSAGE']:
                    print("[Servidor] Cliente solicitó salir")
                    break

                print("[Servidor] Nueva tarea recibida del cliente")
                print(f"[Servidor] Algoritmo: {task.get('algorithm')}")
                print(f"[Servidor] Tamaño del vector: {len(task.get('vector', []))}")
                print(f"[Servidor] Tiempo límite por worker: {task.get('time_limit')}s")

                self.total_time = 0
                # Enviar tarea al Worker 0
                if 0 in self.workers:
                    print("[Servidor] Iniciando tarea con Worker 0")
                    self.workers[0].send(data)
                else:
                    print("[Servidor] Worker 0 no está disponible")
                    error_msg = {'error': 'Worker 0 no está disponible'}
                    conn.send(json.dumps(error_msg).encode())

            except Exception as e:
                print(f"[Servidor] Error en manejo de cliente: {e}")
                break

        print("[Servidor] Cliente desconectado")
        self.client = None
        conn.close()