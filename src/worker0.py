import socket
import threading
import time
import json
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort

stop_flag = threading.Event()

class Worker0:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_0_PORT']))
        self.server_socket.listen(1)
        print("[Worker 0] Iniciado y esperando conexiones...")

    def recv_large_data(self, conn):
        buffer = b""
        while True:
            chunk = conn.recv(8192)
            if not chunk:
                print("[Worker 0] Error: Conexión cerrada inesperadamente.")
                return None
            if b'__END__' in chunk:
                buffer += chunk.split(b'__END__')[0]
                break
            buffer += chunk
        try:
            print(f"[Worker 0] Datos recibidos (algunos): {buffer[:200]}...")  # Registro de datos recibidos
            return json.loads(buffer.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"[Worker 0] Error al decodificar JSON: {e}")
            print(f"[Worker 0] Datos recibidos completos: {buffer}")
            return None

    def send_large_data(self, conn, data):
        serialized_data = json.dumps(data).encode('utf-8')
        conn.sendall(serialized_data)
        conn.sendall(b'__END__')  # Marcamos el final del mensaje

    def sort_vector(self, vector, algorithm, time_limit):
        stop_flag.clear()
        start_time = time.time()
        sort_func = {"mergesort": merge_sort, "heapsort": heap_sort, "quicksort": quick_sort}[algorithm]

        sort_thread = threading.Thread(target=sort_func, args=(vector, start_time, time_limit))
        sort_thread.start()
        elapsed_time = time.time() - start_time
        sort_thread.join(timeout=time_limit)

        if sort_thread.is_alive() and elapsed_time > time_limit:
            stop_flag.set()
            print("[Worker 0] Tiempo límite alcanzado. Delegando a Worker 1.")
            sort_thread.join()
            return False, vector, elapsed_time
        return True, vector, time.time() - start_time

    def handle_client(self, conn):
        try:
            task = self.recv_large_data(conn)
            if task is None:
                return  # Si hubo un error al recibir los datos, terminamos

            source = task.get("source", "client")
            vector, algorithm, time_limit = task["vector"], task["algorithm"], task["time_limit"]
            print(f"[Worker 0] Recibida tarea desde {source} con {len(vector)} elementos, algoritmo: {algorithm}")

            success, vector, elapsed_time = self.sort_vector(vector, algorithm, time_limit)
            if success:
                response = {"vector": vector, "time": elapsed_time, "worker_id": 0}
            else:
                if source == "client":
                    print("[Worker 0] Delegando tarea a Worker 1.")
                    self.delegate_to_worker1(task, conn)
                elif source == "worker_1":
                    print("[Worker 0] Tarea regresada desde Worker 1 no completada.")
                    self.delegate_to_worker1(task, conn)
                return

            self.send_large_data(conn, response)
        except Exception as e:
            print(f"[Worker 0] Error: {e}")
        finally:
            conn.close()

    def delegate_to_worker1(self, task, conn):
        try:
            print("[Worker 0] Conectando a Worker 1...")
            with socket.create_connection((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_1_PORT'])) as worker1_socket:
                task["source"] = "worker_0"
                self.send_large_data(worker1_socket, task)
                response = self.recv_large_data(worker1_socket)
                print(f"[Worker 0] Respuesta recibida de Worker 1: {response}")
                self.send_large_data(conn, response)
        except socket.timeout:
            print("[Worker 0] Tiempo de espera agotado al conectar con Worker 1.")
            response = {"error": "Worker 1 no respondió a tiempo"}
            self.send_large_data(conn, response)
        except Exception as e:
            print(f"[Worker 0] Error al conectar con Worker 1: {e}")
            response = {"error": "Fallo la conexión con Worker 1"}
            self.send_large_data(conn, response)

    def run(self):
        while True:
            try:
                conn, _ = self.server_socket.accept()
                print("[Worker 0] Conexión recibida. Procesando tarea...")
                self.handle_client(conn)
            except Exception as e:
                print(f"[Worker 0] Error: {e}")

if __name__ == '__main__':
    Worker0().run()
