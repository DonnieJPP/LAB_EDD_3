import socket
import threading
import json
import time
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort_worker

def connect_to_server(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    return client_socket

class Worker1:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((CONFIG_PARAMS['SERVER_IP'], CONFIG_PARAMS['WORKER_1_PORT']))
        self.server_socket.listen(5)
        print(f"[Worker 1] Iniciado en {CONFIG_PARAMS['SERVER_IP']}:{CONFIG_PARAMS['WORKER_1_PORT']} y esperando conexiones...")

    def handle_server(self, conn):
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    print("[Worker 1] Servidor desconectado.")
                    break
                print(f"[Worker 1] Datos recibidos del servidor: {data.decode('utf-8')}")
        except socket.error as e:
            print(f"[Worker 1] Error de socket con el servidor: {e}")
        finally:
            conn.close()
            print("[Worker 1] Conexión con el servidor cerrada.")

    def sort_vector(self, vector, algorithm, time_limit, task_dict):
        """
        Realiza la ordenación del vector según el algoritmo especificado.
        """
        start_time = time.time()
        if algorithm == "quicksort":
            sorted_vector, task_dict = quick_sort_worker(vector, time_limit, task_dict, worker_id=1)
        else:
            sort_func = {"mergesort": merge_sort, "heapsort": heap_sort}.get(algorithm)
            if not sort_func:
                raise ValueError(f"[Worker 1] Algoritmo no soportado: {algorithm}")
            sort_thread = threading.Thread(target=sort_func, args=(vector,))
            sort_thread.start()
            sort_thread.join(timeout=time_limit)
            task_dict["estado"] = not sort_thread.is_alive()
            sorted_vector = vector
        elapsed_time = time.time() - start_time
        return sorted_vector, task_dict, elapsed_time

    def handle_client(self, conn):
        """
        Gestiona la conexión con un cliente.
        """
        try:
            data = self.recv_large_data(conn)
            if not data:
                return
            algorithm = data.get('algorithm')
            time_limit = data.get('time_limit')
            vector = data.get('vector')
            task_dict = data.get('task_dict', {"estado": False, "progress": 0, "stack": []})
            print(f"[Worker 1] Recibida tarea: {algorithm}, progreso actual: {task_dict['progress']:.2f}%")
            print(f"[Worker 1] Estado inicial del vector (primeros 100): {vector[:100]}")
            vector, task_dict, elapsed_time = self.sort_vector(vector, algorithm, time_limit, task_dict)
            if task_dict["estado"]:
                print("[Worker 1] Tarea completada exitosamente")
                response = {
                    'vector': vector,
                    'time': elapsed_time,
                    'worker_id': 1,
                    'progress': 100.0
                }
            else:
                print(f"[Worker 1] Tiempo límite alcanzado, progreso: {task_dict['progress']:.2f}%")
                response = {
                    'incomplete': True,
                    'vector': vector,
                    'time': elapsed_time,
                    'task_dict': task_dict
                }
            print(f"[Worker 1] Estado final del vector (primeros 5): {vector[:5]}")
            self.send_large_data(conn, response)
        except Exception as e:
            print(f"[Worker 1] Error al manejar cliente: {e}")
        finally:
            conn.close()
            print("[Worker 1] Conexión cerrada")

    def recv_large_data(self, conn):
        """
        Recibe un mensaje JSON largo desde un socket, en múltiples fragmentos.
        """
        buffer = b""
        while True:
            chunk = conn.recv(8192)
            if not chunk:
                print("[Worker 1] Conexión cerrada inesperadamente.")
                return None
            buffer += chunk
            if b'_END_' in buffer:
                buffer = buffer.split(b'_END_')[0]
                break
        try:
            return json.loads(buffer.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"[Worker 1] Error al decodificar JSON: {e}")
            return None

    def send_large_data(self, conn, data):
        """
        Envía un mensaje JSON largo a través de un socket.
        """
        try:
            serialized_data = json.dumps(data).encode('utf-8')
            conn.sendall(serialized_data + b'_END_')
            print("[Worker 1] Datos enviados correctamente")
        except Exception as e:
            print(f"[Worker 1] Error al enviar datos: {e}")

    def run(self):
        """
        Inicia el servidor y espera conexiones.
        """
        # Conectar a Worker 0
        worker0_conn = connect_to_server(CONFIG_PARAMS['SERVER_IP'], CONFIG_PARAMS['WORKER_0_PORT'])
        threading.Thread(target=self.handle_server, args=(worker0_conn,)).start()

        # Conectar al servidor principal
        server_conn = connect_to_server(CONFIG_PARAMS['SERVER_IP'], CONFIG_PARAMS['SERVER_PORT'])
        threading.Thread(target=self.handle_server, args=(server_conn,)).start()

        while True:
            conn, addr = self.server_socket.accept()
            print(f"[Worker 1] Nueva conexión aceptada de {addr}")
            threading.Thread(target=self.handle_client, args=(conn,)).start()

if __name__ == '__main__':
    Worker1().run()