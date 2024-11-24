import socket
import json
import time
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort

def recv_large_data(socket):
    buffer = b""
    while True:
        chunk = socket.recv(8192)
        if not chunk:
            print("[Worker 0] Conexión cerrada inesperadamente.")
            return None
        buffer += chunk
        if b'__END__' in buffer:
            buffer = buffer.split(b'__END__')[0]
            break

    try:
        return json.loads(buffer.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"[Worker 0] Error al decodificar JSON: {e}")
        print(f"[Worker 0] Datos recibidos: {buffer}")
        return None

def send_large_data(socket, data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
        socket.sendall(serialized_data + b'__END__')
    except Exception as e:
        print(f"[Worker 0] Error al enviar datos: {e}")

def timed_sort(algorithm, vector, time_limit):
    start_time = time.time()
    if algorithm == 'mergesort':
        merge_sort(vector, start_time, time_limit)
    elif algorithm == 'heapsort':
        heap_sort(vector, start_time, time_limit)
    elif algorithm == 'quicksort':
        vector = quick_sort(vector, start_time, time_limit)
    return vector

def worker(worker_id, port):
    worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_socket.bind((CONFIG_PARAMS['SERVER_IP_ADDRESS'], port))
    worker_socket.listen(5)
    print(f"[Worker {worker_id}] Esperando conexiones...")

    while True:
        client_socket, addr = worker_socket.accept()
        print(f"[Worker {worker_id}] Conexión aceptada de {addr}")
        try:
            data = recv_large_data(client_socket)
            if data:
                algorithm = data['algorithm']
                time_limit = data['time_limit']
                vector = data['vector']

                print(f"[Worker {worker_id}] Datos recibidos: algoritmo={algorithm}, tiempo límite={time_limit}, vector (primeros 10 elementos)={vector[:10]}")

                start_time = time.time()
                vector = timed_sort(algorithm, vector, time_limit)
                end_time = time.time()
                elapsed_time = end_time - start_time

                response = {
                    'vector': vector,
                    'time': elapsed_time,
                    'worker_id': worker_id
                }
                send_large_data(client_socket, response)
        except Exception as e:
            print(f"[Worker {worker_id}] Error: {e}")
        finally:
            client_socket.close()

if __name__ == '__main__':
    worker_id = 0
    port = CONFIG_PARAMS[f'WORKER_{worker_id}_PORT']
    worker(worker_id, port)