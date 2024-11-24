import socket
import json
import threading
import time
from config import CONFIG_PARAMS
from ordenamientos import merge_sort, heap_sort, quick_sort


def sort_task_partial(task, progress_index):
    """
    Ordena parcialmente un vector desde un índice dado.
    """
    vector = task["vector"]
    algorithm = task["algorithm"]
    start_time = time.time()

    if algorithm == "mergesort":
        merge_sort(vector[progress_index:])
    elif algorithm == "heapsort":
        heap_sort(vector[progress_index:])
    elif algorithm == "quicksort":
        quick_sort(vector, progress_index, len(vector) - 1)

    elapsed_time = time.time() - start_time
    return elapsed_time, vector


def worker(port, next_port, worker_id):
    """
    Worker principal que procesa las tareas y alterna con el siguiente worker en caso de no completarlas.
    """
    worker_name = f"worker_{worker_id}"  # Nombre único del worker
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", port))
    sock.listen(1)
    print(f"[{worker_name}] Activo en el puerto {port}. Esperando tareas...")

    while True:
        conn, _ = sock.accept()
        try:
            data = conn.recv(4096)
            if not data:
                continue

            task = json.loads(data.decode('utf-8'))
            vector = task["vector"]
            progress_index = task.get("progress_index", 0)
            time_limit = task["time"]

            print(f"[{worker_name}] Recibió tarea con {len(vector)} elementos. Progreso: {progress_index}/{len(vector)}")

            start_time = time.time()
            elapsed_time, vector = sort_task_partial(task, progress_index)
            total_elapsed = elapsed_time + (time.time() - start_time)

            if total_elapsed < time_limit:
                result = {"vector": vector, "progress_index": len(vector), "time": total_elapsed, "completed": True}
                conn.sendall(json.dumps(result).encode('utf-8'))
                print(f"[{worker_name}] Completó la tarea en {total_elapsed:.2f} segundos.")
            else:
                next_task = {
                    "algorithm": task["algorithm"],
                    "vector": vector,
                    "progress_index": progress_index,
                    "time": time_limit - total_elapsed,
                }
                print(f"[{worker_name}] Tiempo agotado. Delegando tarea al siguiente worker.")
                next_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                next_sock.connect(("127.0.0.1", next_port))
                next_sock.sendall(json.dumps(next_task).encode('utf-8'))
                next_sock.close()
        except Exception as e:
            print(f"[{worker_name}] Error procesando la tarea: {e}")
        finally:
            conn.close()
