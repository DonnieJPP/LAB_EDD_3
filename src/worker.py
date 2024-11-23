import socket
import json
import time
from ordenamientos import mergesort, quicksort, heapsort

def sort_task(task, time_limit):
    arr = task["vector"]
    algo = task["algorithm"]
    start = time.time()

    if algo == "mergesort":
        mergesort(arr)
    elif algo == "quicksort":
        arr[:] = quicksort(arr)
    elif algo == "heapsort":
        arr[:] = heapsort(arr)

    elapsed = time.time() - start
    return elapsed <= time_limit, arr, elapsed

def worker(port, next_port=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", port))
    sock.listen(1)
    print(f"Worker activo en el puerto {port}...")

    while True:
        conn, _ = sock.accept()
        data = conn.recv(2048)
        if not data:
            continue

        task = json.loads(data.decode('utf-8'))
        success, sorted_vector, elapsed = sort_task(task, task["time"])

        if success or not next_port:
            conn.sendall(json.dumps({"status": "done", "vector": sorted_vector, "time": elapsed}).encode('utf-8'))
        else:
            next_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            next_sock.connect(("127.0.0.1", next_port))
            next_sock.sendall(json.dumps({"vector": sorted_vector, "time": task["time"] - elapsed}).encode('utf-8'))
            next_sock.close()

if __name__ == '__main__':
    worker(8082, next_port=8083)