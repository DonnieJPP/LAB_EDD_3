import socket
import threading
import time
import json
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort

class Worker1:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_1_PORT']))
        self.server_socket.listen(1)
        print("[Worker 1] Iniciado y esperando conexiones...")

    def send_large_data(socket, data):
        try:
            serialized_data = json.dumps(data).encode('utf-8')
            socket.sendall(serialized_data)
            socket.sendall(b'__END__')  # Marcador para indicar el fin de los datos
        except Exception as e:
            print(f"[Worker] Error al enviar datos: {e}")

    def sort_vector(self, vector, algorithm, time_limit):
        start_time = time.time()
        sort_func = {"mergesort": merge_sort, "heapsort": heap_sort, "quicksort": quick_sort}[algorithm]

        sort_thread = threading.Thread(target=sort_func, args=(vector,))
        sort_thread.start()
        sort_thread.join(timeout=time_limit)

        elapsed_time = time.time() - start_time
        if sort_thread.is_alive():
            print("[Worker 1] Tiempo límite alcanzado.")
            return False, elapsed_time
        return True, elapsed_time

    def handle_client(self, conn):
        try:
            task = self.recv_large_data(conn)
            vector, algorithm, time_limit = task["vector"], task["algorithm"], task["time_limit"]
            success, elapsed_time = self.sort_vector(vector, algorithm, time_limit)

            response = {
                "vector": vector,
                "time": elapsed_time,
                "worker_id": 1 if success else -1
            }
            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"[Worker 1] Error: {e}")
        finally:
            conn.close()

    def run(self):
        while True:
            conn, _ = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()

if __name__ == '__main__':
    Worker1().run()
