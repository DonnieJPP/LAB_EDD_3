import socket
import json
import time
from config import CONFIG_PARAMS
from ordenamientos import mergesort, quicksort, heapsort


def sort_task(task, time_limit):
    arr = task["vector"]
    algo = task["algorithm"]
    start = time.time()

    # Aplicar el algoritmo de ordenamiento correspondiente
    if algo == "mergesort":
        mergesort(arr)
    elif algo == "quicksort":
        arr[:] = quicksort(arr)
    elif algo == "heapsort":
        arr[:] = heapsort(arr)

    elapsed = time.time() - start
    return elapsed <= time_limit, arr, elapsed

# Función principal para cada worker
def worker(port, next_port=None):
    # Crear un socket para el worker
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", port))  # Escuchar en todas las interfaces en el puerto dado
    sock.listen(1)
    print(f"Worker activo en el puerto {port}...")

    while True:
        conn, _ = sock.accept()
        data = conn.recv(4096)
        if not data:
            continue

        task = json.loads(data.decode('utf-8'))
        print(f"Worker {port} recibió datos: {len(task['vector'])} elementos, {task['time']} segundos restantes")

        start_time = time.time()
        success, sorted_vector, elapsed_time = sort_task(task, task["time"])

        if success or not next_port:
            result = {"vector": sorted_vector, "time": elapsed_time}
            conn.sendall(json.dumps(result).encode('utf-8'))
            print(f"Worker {port} completó la tarea en {elapsed_time:.2f} segundos")
        else:
            # Si el tiempo se agotó, pasar los datos al siguiente worker
            remaining_time = task["time"] - elapsed_time
            print(f"Tiempo agotado en Worker {port}. Enviando datos al siguiente worker {next_port}")
            next_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            next_sock.connect((CONFIG_PARAMS['WORKER_1_IP'], CONFIG_PARAMS['WORKER_1_PORT']))  # Conectar a worker_1
            next_task = {"algorithm": task["algorithm"], "time": remaining_time, "vector": sorted_vector}
            next_sock.sendall(json.dumps(next_task).encode('utf-8'))
            next_sock.close()

        conn.close()

if __name__ == '__main__':
    worker(CONFIG_PARAMS['WORKER_0_PORT'], CONFIG_PARAMS['WORKER_1_PORT'])