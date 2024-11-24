import socket
import json
import time
from ordenamientos import merge_sort, heap_sort, quick_sort
from config import CONFIG_PARAMS
class Worker:
    def _init_(self, worker_id):
        self.worker_id = worker_id
        self.server_host = CONFIG_PARAMS['SERVER_IP_ADDRESS']
        self.server_port = CONFIG_PARAMS['SERVER_PORT']
        self.connected_to_server = False
        print(f"[Worker {self.worker_id}] Iniciando...")
        
    def connect_to_server(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_host, self.server_port))
            self.connected_to_server = True
            print(f"[Worker {self.worker_id}] Conectado exitosamente al servidor en {self.server_host}:{self.server_port}")
            return sock
        except Exception as e:
            print(f"[Worker {self.worker_id}] Error al conectar con el servidor: {e}")
            return None

    def process_vector(self, vector, algorithm, time_limit, progress=0):
        print(f"[Worker {self.worker_id}] Iniciando ordenamiento con algoritmo {algorithm}")
        print(f"[Worker {self.worker_id}] Tiempo límite: {time_limit} segundos")
        print(f"[Worker {self.worker_id}] Progreso recibido: {progress}%")
        
        start_time = time.time()
        sorted_vector = vector.copy()
        
        try:
            # Implementar el control de tiempo con más detalle
            if algorithm == "mergesort":
                merge_sort(sorted_vector)
            elif algorithm == "heapsort":
                heap_sort(sorted_vector)
            elif algorithm == "quicksort":
                quick_sort(sorted_vector, 0, len(sorted_vector) - 1)
                
            elapsed_time = time.time() - start_time
            
            if elapsed_time <= time_limit:
                print(f"[Worker {self.worker_id}] Ordenamiento completado en {elapsed_time:.2f} segundos")
                return True, sorted_vector, elapsed_time
            else:
                print(f"[Worker {self.worker_id}] Tiempo límite excedido. Enviando progreso parcial")
                # Calcular progreso aproximado
                current_progress = (time_limit / elapsed_time) * 100
                return False, sorted_vector, time_limit
                
        except Exception as e:
            print(f"[Worker {self.worker_id}] Error durante el ordenamiento: {e}")
            return False, vector, time.time() - start_time

    def start(self):
        print(f"[Worker {self.worker_id}] Iniciando servicio...")
        sock = self.connect_to_server()
        if not sock:
            return
        
        # Identificarse con el servidor
        sock.send(f"worker_{self.worker_id}".encode())
        print(f"[Worker {self.worker_id}] Identificación enviada al servidor")
        
        while True:
            try:
                print(f"[Worker {self.worker_id}] Esperando nueva tarea...")
                data = sock.recv(4096)
                if not data:
                    print(f"[Worker {self.worker_id}] Conexión cerrada por el servidor")
                    break
                    
                task = json.loads(data.decode())
                vector = task['vector']
                algorithm = task['algorithm']
                time_limit = task['time_limit']
                
                # Obtener el progreso previo si existe
                progress = task.get('progress', 0)
                total_time = task.get('total_time', 0)
                
                print(f"[Worker {self.worker_id}] Nueva tarea recibida:")
                print(f"[Worker {self.worker_id}] - Tamaño del vector: {len(vector)}")
                print(f"[Worker {self.worker_id}] - Algoritmo: {algorithm}")
                print(f"[Worker {self.worker_id}] - Tiempo límite: {time_limit}")
                print(f"[Worker {self.worker_id}] - Progreso previo: {progress}%")
                
                completed, result_vector, time_used = self.process_vector(
                    vector, algorithm, time_limit, progress
                )
                
                if completed:
                    response = {
                        'status': 'complete',
                        'vector': result_vector,
                        'time_used': total_time + time_used,
                        'completed_by': self.worker_id
                    }
                    print(f"[Worker {self.worker_id}] Tarea completada exitosamente")
                    print(f"[Worker {self.worker_id}] Tiempo total usado: {total_time + time_used:.2f}s")
                else:
                    response = {
                        'status': 'incomplete',
                        'partial_vector': result_vector,
                        'time_used': time_used,
                        'algorithm': algorithm,
                        'remaining_time': max(0, time_limit - time_used),
                        'progress': progress + ((100 - progress) * (time_used / time_limit))
                    }
                    print(f"[Worker {self.worker_id}] Tiempo agotado, enviando progreso parcial")
                    print(f"[Worker {self.worker_id}] Progreso estimado: {response['progress']:.2f}%")
                
                print(f"[Worker {self.worker_id}] Enviando respuesta al servidor")
                sock.send(json.dumps(response).encode())
                
            except Exception as e:
                print(f"[Worker {self.worker_id}] Error en el procesamiento: {e}")
                break
                
        sock.close()
        print(f"[Worker {self.worker_id}] Servicio finalizado")