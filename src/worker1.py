import socket
import threading
import json
import time
from config import CONFIG_PARAMS
from sorting_algorithms import merge_sort, heap_sort, quick_sort

stop_flag = threading.Event()

def recv_large_data(conn):
    buffer = b""
    while True:
        chunk = conn.recv(8192)
        if not chunk:
            print("[Worker 1] Conexión cerrada inesperadamente.")
            return None
        buffer += chunk
        if b'__END__' in buffer:
            buffer = buffer.split(b'__END__')[0]
            break

    try:
        print(f"[Worker 1] Datos recibidos (algunos): {buffer[:200]}...")  # Registro de datos recibidos
        return json.loads(buffer.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"[Worker 1] Error al decodificar JSON: {e}")
        print(f"[Worker 1] Datos recibidos completos: {buffer}")
        return None

def send_large_data(conn, data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
        conn.sendall(serialized_data + b'__END__')
        print(f"[Worker 1] Datos enviados correctamente (algunos): {serialized_data[:200]}...")
    except Exception as e:
        print(f"[Worker 1] Error al enviar datos: {e}")

def truncate_data(data, length=200):
    """Función auxiliar para truncar los datos impresos."""
    data_str = json.dumps(data)
    if len(data_str) > length:
        return data_str[:length] + '...'
    return data_str

def sort_vector(vector, algorithm, time_limit):
    start_time = time.time()
    stop_flag.clear()
    
    sort_func = {"mergesort": merge_sort, "heapsort": heap_sort, "quicksort": quick_sort}[algorithm]
    sort_thread = threading.Thread(target=sort_func, args=(vector, start_time, time_limit))
    sort_thread.start()
    sort_thread.join(timeout=time_limit)
    
    elapsed_time = time.time() - start_time
    if sort_thread.is_alive() and elapsed_time > time_limit:
        stop_flag.set()
        print(f"[Worker 1] Tiempo límite alcanzado. Devolviendo tarea al otro worker.")
        return False, vector, elapsed_time  # Indica que no se completó a tiempo
    print(f"[Worker 1] Ordenamiento completado en {elapsed_time} segundos.")
    return True, vector, elapsed_time

def worker_1():
    worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_socket.bind((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_1_PORT']))
    worker_socket.listen(1)
    print("[Worker 1] Esperando tareas del Worker 0...")

    while True:
        conn, _ = worker_socket.accept()
        try:
            task = recv_large_data(conn)
            if task:
                print(f"[Worker 1] Tarea recibida: {truncate_data(task)}")
                success, vector, elapsed_time = sort_vector(task['vector'], task['algorithm'], task['time_limit'])
                if success:
                    # Conectar directamente al cliente y enviar la respuesta
                    print(f"[Worker 1] Ordenamiento completado con éxito en {elapsed_time} segundos. Enviando respuesta al cliente.")
                    with socket.create_connection((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['CLIENT_PORT'])) as client_socket:
                        response = {'vector': vector, 'time': elapsed_time, 'worker_id': 1}
                        send_large_data(client_socket, response)
                        print("[Worker 1] Resultado enviado al cliente.")
                else:
                    # Devolver tarea al Worker 0
                    print("[Worker 1] No se completó a tiempo. Devolviendo tarea al Worker 0.")
                    with socket.create_connection((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_0_PORT'])) as worker0_socket:
                        task['source'] = 'worker_1'  # Actualizar la fuente para indicar que viene de worker_1
                        send_large_data(worker0_socket, task)
                        print("[Worker 1] Tarea devuelta al Worker 0.")
        except Exception as e:
            print(f"[Worker 1] Error: {e}")
        finally:
            conn.close()

if __name__ == '__main__':
    worker_1()
