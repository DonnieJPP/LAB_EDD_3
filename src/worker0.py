import socket
import threading
import time
import json
from client import recv_large_data
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort

class Worker0:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_0_PORT']))
        self.server_socket.listen(1)
        print("[Worker 0] Iniciado y esperando conexiones...")

    def recv_large_data(conn):
        """Recibe un mensaje JSON largo desde un socket, en múltiples fragmentos."""
        buffer = b""
        while True:
            chunk = conn.recv(4096)
            if b'__END__' in chunk:
                buffer += chunk.split(b'__END__')[0]
                break
            buffer += chunk
        return json.loads(buffer.decode('utf-8'))    

    def sort_vector(self, vector, algorithm, time_limit):
        start_time = time.time()
        sort_func = {"mergesort": merge_sort, "heapsort": heap_sort, "quicksort": quick_sort}[algorithm]

        sort_thread = threading.Thread(target=sort_func, args=(vector,))
        sort_thread.start()
        sort_thread.join(timeout=time_limit)

        elapsed_time = time.time() - start_time
        if sort_thread.is_alive():
            print("[Worker 0] Tiempo límite alcanzado. Delegando a Worker 1.")
            return False, elapsed_time
        return True, elapsed_time

    def handle_client(self, conn):
        try:
            # Usa recv_large_data para recibir tareas extensas
            task = recv_large_data(conn)
            vector, algorithm, time_limit = task["vector"], task["algorithm"], task["time_limit"]
            print(f"[Worker 0] Recibida tarea con {len(vector)} elementos, algoritmo: {algorithm}")

            success, elapsed_time = self.sort_vector(vector, algorithm, time_limit)
            if success:
                response = {"vector": vector, "time": elapsed_time, "worker_id": 0}
            else:
                # Delegar a Worker 1
                worker1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                worker1_socket.connect((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_1_PORT']))
                worker1_socket.sendall(json.dumps(task).encode('utf-8'))
                response = json.loads(worker1_socket.recv(4096).decode('utf-8'))
                worker1_socket.close()

            conn.sendall(json.dumps(response).encode('utf-8'))  # Responder al cliente
        except Exception as e:
            print(f"[Worker 0] Error: {e}")
        finally:
            conn.close()


    def run(self):
        while True:
            conn, _ = self.server_socket.accept()  # Espera por conexiones
            threading.Thread(target=self.handle_client, args=(conn,)).start()

if __name__ == '__main__':
    Worker0().run()
