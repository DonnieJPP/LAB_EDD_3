import socket
import threading
import json
import time
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort_worker

class Worker0:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((CONFIG_PARAMS['SERVER_IP'], CONFIG_PARAMS['WORKER_0_PORT']))
        self.server_socket.listen(5)
        print(f"[Worker 0] Iniciado en {CONFIG_PARAMS['SERVER_IP']}:{CONFIG_PARAMS['WORKER_0_PORT']} y esperando conexiones...")

    def handle_worker1(self, conn):
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    print("[Worker 0] Worker 1 desconectado.")
                    break
                print(f"[Worker 0] Datos recibidos de Worker 1: {data.decode('utf-8')}")
        except socket.error as e:
            print(f"[Worker 0] Error de socket con Worker 1: {e}")
        finally:
            conn.close()
            print("[Worker 0] Conexión con Worker 1 cerrada.")

    def sort_vector(self, vector, algorithm, time_limit, task_dict=None):
        """
        Realiza el ordenamiento utilizando el algoritmo especificado dentro del límite de tiempo.
        """
        start_time = time.time()
        if algorithm == "quicksort" and task_dict:
            vector, task_dict = quick_sort_worker(vector, time_limit, task_dict, worker_id=0)
            elapsed_time = time.time() - start_time
            return task_dict["estado"], elapsed_time, vector, task_dict
        else:
            sort_func = {"mergesort": merge_sort, "heapsort": heap_sort, "quicksort": quick_sort_worker}[algorithm]
            sort_thread = threading.Thread(target=sort_func, args=(vector,))
            sort_thread.start()
            sort_thread.join(timeout=time_limit)
            elapsed_time = time.time() - start_time
            if sort_thread.is_alive():
                print("[Worker 0] Tiempo límite alcanzado.")
                return False, elapsed_time, vector, None
            return True, elapsed_time, vector, None

    def handle_client(self, conn):
        """
        Maneja la conexión con un cliente.
        """
        try:
            task = self.recv_large_data(conn)
            if not task:
                return
            algorithm = task.get('algorithm')
            time_limit = task.get('time_limit')
            vector = task.get('vector')
            task_dict = task.get('task_dict', {"estado": False, "progress": 0, "stack": []})
            print(f"[Worker 0] Recibida tarea con {len(vector)} elementos, algoritmo: {algorithm}")
            success, elapsed_time, sorted_vector, updated_task_dict = self.sort_vector(
                vector, algorithm, time_limit, task_dict
            )
            if success:
                response = {
                    'vector': sorted_vector,
                    'time': elapsed_time,
                    'worker_id': 0,
                    'progress': 100.0
                }
            else:
                response = {
                    'incomplete': True,
                    'vector': sorted_vector,
                    'time': elapsed_time,
                    'task_dict': updated_task_dict or task_dict
                }
            self.send_large_data(conn, response)
        except Exception as e:
            print(f"[Worker 0] Error: {e}")
        finally:
            conn.close()
            print("[Worker 0] Conexión cerrada")

    def recv_large_data(self, conn):
        """
        Recibe un mensaje JSON largo desde un socket, en múltiples fragmentos.
        """
        buffer = b""
        while True:
            chunk = conn.recv(8192)
            if not chunk:
                print("[Worker 0] Conexión cerrada inesperadamente.")
                return None
            buffer += chunk
            if b'_END_' in buffer:
                buffer = buffer.split(b'_END_')[0]
                break
        try:
            return json.loads(buffer.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"[Worker 0] Error al decodificar JSON: {e}")
            return None

    def send_large_data(self, conn, data):
        """
        Envía un mensaje JSON largo a través de un socket.
        """
        try:
            serialized_data = json.dumps(data).encode('utf-8')
            conn.sendall(serialized_data + b'_END_')
            print("[Worker 0] Datos enviados correctamente")
        except Exception as e:
            print(f"[Worker 0] Error al enviar datos: {e}")

    def run(self):
        """
        Ejecuta el servidor para manejar múltiples clientes.
        """
        while True:
            conn, addr = self.server_socket.accept()
            print(f"[Worker 0] Nueva conexión aceptada de {addr}")
            threading.Thread(target=self.handle_client, args=(conn,)).start()

if __name__ == '__main__':
    Worker0().run()