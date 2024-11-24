import socket
import threading
import time
import json
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort

stop_flag = threading.Event()

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

    def recv_large_data(conn):
        """Recibe datos grandes en fragmentos."""
        buffer = b""
        while True:
            chunk = conn.recv(8192)
            if b'__END__' in chunk:
                buffer += chunk.split(b'__END__')[0]
                break
            buffer += chunk
        return json.loads(buffer.decode('utf-8'))

    def sort_vector(self, vector, algorithm, time_limit):
        stop_flag.clear()
        start_time = time.time()
        sort_func = {"mergesort": merge_sort, "heapsort": heap_sort, "quicksort": quick_sort}[algorithm]

        sort_thread = threading.Thread(target=sort_func, args=(vector,))
        sort_thread.start()
        sort_thread.join(timeout=time_limit)

        elapsed_time = time.time() - start_time
        if sort_thread.is_alive():
            print("[Worker 1] Tiempo límite alcanzado. Delegando al Worker 1")
            stop_flag.set()
            sort_thread.join()
            return False, vector, elapsed_time
        return True, vector,time.time() - start_time

    def handle_worker(self, conn):
        try:
            task = self.recv_large_data(conn)
            vector, algorithm, time_limit = task["vector"], task["algorithm"], task["time_limit"]
            print(f"[Worker 1] Recibida tarea con {len(vector)} elementos, algoritmo: {algorithm}")
            success, vector ,elapsed_time = self.sort_vector(vector, algorithm, time_limit)
            if success:
                response = {"vector": vector, "time": elapsed_time, "worker_id": 1}
            else:
                # Delegar a Worker 0
                print("[Worker 1] Tiempo límite alcanzado. Devolviendo a Worker 0.")
                response = json.loads(worker0_socket.recv(8192).decode('utf-8'))
                worker0_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                worker0_socket.connect((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_0_PORT']))
                self.send_large_data(worker0_socket, response)
                worker0_socket.close() 
                return

            conn.sendall(json.dumps(response).encode('utf-8'))  # Responder al cliente
            conn.sendall(b'__END__')  
        except Exception as e:
            print(f"[Worker 1] Error: {e}")
        finally:
            conn.close()

    def run(self):
        while True:
            conn, address = self.server_socket.accept()
            threading.Thread(target=self.handle_worker, args=(conn,)).start()

if __name__ == '__main__':
    Worker1().run()
