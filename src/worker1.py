
import socket
import json
import time
from config import CONFIG_PARAMS
from sorting_algorithms import quicksort_partial, mergesort_partial, heapsort_partial

def send_large_data(conn, data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
        conn.sendall(serialized_data + b'__END__')
        print(f"[Worker 1] Datos enviados correctamente.")
    except Exception as e:
        print(f"[Worker 1] Error al enviar datos: {e}")

def recv_large_data(conn):
    buffer = b""
    while True:
        try:
            chunk = conn.recv(8192)
            if not chunk:
                print("[Worker 1] Conexión cerrada inesperadamente.")
                return None
            buffer += chunk
            if b'__END__' in buffer:
                buffer = buffer.split(b'__END__')[0]
                break
        except Exception as e:
            print(f"[Worker 1] Error al recibir datos: {e}")
            return None

    try:
        return json.loads(buffer.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"[Worker 1] Error al decodificar datos: {e}")
        return None

def process_task(data, progress, algorithm, time_limit, task_dict):
    start_time = time.time()
    while time.time() - start_time < time_limit:
        print(f"[Worker 1] Progreso actual: {progress}, Tiempo transcurrido: {time.time() - start_time:.2f} s")
        print(f"[Worker 1] Vector parcial: {data[:10]}")  # Mostrar los primeros 10 elementos para seguimiento

        if algorithm == "quicksort":
            data, progress, task_dict = quicksort_partial(data, progress, len(data) - 1, time_limit, task_dict)
        elif algorithm == "mergesort":
            data, progress, task_dict = mergesort_partial(data, progress, time_limit, task_dict)
        elif algorithm == "heapsort":
            data, progress, task_dict = heapsort_partial(data, progress, time_limit, task_dict)

        if progress >= len(data):
            print(f"[Worker 1] Ordenamiento completado.")
            return data, progress, task_dict, True

    print(f"[Worker 1] Tiempo límite alcanzado. Progreso actual: {progress}")
    return data, progress, task_dict, False

def worker1_program():
    print("[Worker 1] Iniciado y esperando conexión de Worker 0...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((CONFIG_PARAMS['HOST_WORKER_1'], CONFIG_PARAMS['PORT_WORKER_1']))
        server.listen()

        while True:
            conn_worker_0, addr = server.accept()
            print(f"[Worker 1] Conexión aceptada de Worker 0 en {addr}.")

            task = recv_large_data(conn_worker_0)
            if not task:
                print("[Worker 1] No se recibió ninguna tarea. Cerrando conexión.")
                conn_worker_0.close()
                continue

            print(f"[Worker 1] Tarea recibida: Algoritmo: {task['algorithm']}, progreso: {task['progress']}")
            algorithm = task["algorithm"]
            data = task["data"]
            progress = task.get("progress", 0)
            time_limit = task["time_limit"]
            task_dict = task.get("task_dict", {"estado": True})

            data, progress, task_dict, completed = process_task(data, progress, algorithm, time_limit, task_dict)
            if completed:
                print("[Worker 1] Trabajo completado. Enviando datos a Worker 0...")
                send_large_data(conn_worker_0, {"data": data, "progress": progress, "completed": True, "worker": 1, "time_taken": time.time()})
            else:
                print("[Worker 1] No se completó el trabajo. Devolviendo a Worker 0...")
                send_large_data(conn_worker_0, {"data": data, "progress": progress, "completed": False})

            conn_worker_0.close()

if __name__ == "__main__":
    worker1_program()
