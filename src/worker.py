import socket
import json
import time
import sys
import multiprocessing
from ordenamientos import merge_sort, heap_sort, quick_sort


def sort_task(task, time_limit):
    """
    Ejecuta el algoritmo de ordenamiento y mide el tiempo de ejecución.
    """
    vector = task["vector"]
    algorithm = task["algorithm"]

    start_time = time.time()
    if algorithm == "mergesort":
        merge_sort(vector)
    elif algorithm == "heapsort":
        heap_sort(vector)
    elif algorithm == "quicksort":
        quick_sort(vector, 0, len(vector) - 1)

    elapsed_time = time.time() - start_time
    return elapsed_time <= time_limit, vector, elapsed_time


def worker(port, next_port=None, worker_id=0):
    """
    Función principal para el worker.
    """
    worker_name = f"worker_{worker_id}"  # Nombre único del worker
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", port))
    sock.listen(1)
    print(f"[{worker_name}] Activo y esperando tareas en el puerto {port}...")

    while True:
        conn, _ = sock.accept()
        try:
            buffer = b""
            while True:
                part = conn.recv(4096)
                if not part:
                    break
                buffer += part

            task = json.loads(buffer.decode("utf-8"))
            print(f"[{worker_name}] Tarea recibida con {len(task['vector'])} elementos.")

            # Ejecutar tarea
            success, sorted_vector, elapsed_time = sort_task(task, task["time"])
            if success:
                result = {"vector": sorted_vector, "time": elapsed_time}
                conn.sendall(json.dumps(result).encode("utf-8"))
                print(f"[{worker_name}] Tarea completada en {elapsed_time:.2f} segundos.")
            elif next_port:
                print(f"[{worker_name}] Tiempo agotado. Pasando al siguiente worker.")
                next_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                next_sock.connect(("127.0.0.1", next_port))
                next_task = {
                    "algorithm": task["algorithm"],
                    "time": task["time"],  # Mantener el mismo tiempo
                    "vector": sorted_vector,
                }
                next_sock.sendall(json.dumps(next_task).encode("utf-8"))
                next_sock.close()
            else:
                print(f"[{worker_name}] No hay siguiente worker. Reintentando...")
                conn.sendall(json.dumps({"error": "No workers available."}).encode("utf-8"))
        except Exception as e:
            print(f"[{worker_name}] Error al procesar la tarea: {e}")
        finally:
            conn.close()


def start_workers(worker_count, base_port):
    """
    Lanza automáticamente varios workers como procesos.
    """
    processes = []
    for i in range(worker_count):
        port = base_port + i
        next_port = base_port + ((i + 1) % worker_count)  # Conexión cíclica
        worker_id = i
        print(f"Iniciando worker_{worker_id} en puerto {port}, conectado al puerto {next_port}.")
        process = multiprocessing.Process(target=worker, args=(port, next_port, worker_id))
        process.start()
        processes.append(process)
    return processes


if __name__ == "__main__":
    WORKER_COUNT = 2  # Número de workers
    BASE_PORT = 8082  # Puerto inicial

    # Iniciar workers automáticamente
    print(f"Iniciando {WORKER_COUNT} workers...")
    processes = start_workers(WORKER_COUNT, BASE_PORT)

    print("Sistema en ejecución. Presiona Ctrl+C para detener.")
    try:
        while True:
            time.sleep(1)  # Mantén el script principal vivo
    except KeyboardInterrupt:
        print("\nDeteniendo todos los workers...")
        for p in processes:
            p.terminate()
        print("Sistema detenido.")
