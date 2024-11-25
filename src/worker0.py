
import socket
import json
import time
from config import CONFIG_PARAMS
from sorting_algorithms import quicksort_partial, mergesort_partial, heapsort_partial


def send_large_data(socket, data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
        socket.sendall(serialized_data + b'__END__')
    except Exception as e:
        print(f"[Worker 0] Error al enviar datos: {e}")


def recv_large_data(socket):
    buffer = b""
    while True:
        try:
            chunk = socket.recv(8192)
            if not chunk:
                print("[Worker 0] Conexión cerrada inesperadamente.")
                return None
            buffer += chunk
            if b'__END__' in buffer:
                buffer = buffer.split(b'__END__')[0]
                break
        except Exception as e:
            print(f"[Worker 0] Error al recibir datos: {e}")
            return None

    try:
        return json.loads(buffer.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"[Worker 0] Error al decodificar datos: {e}")
        return None


def process_task(data, progress, algorithm, time_limit, task_dict):
    """
    Procesa la tarea utilizando el algoritmo de ordenamiento.
    """
    start_time = time.time()
    while time.time() - start_time < time_limit:
        if algorithm == "quicksort":
            data, progress, task_dict = quicksort_partial(data, progress, len(data) - 1, time_limit, task_dict)
        elif algorithm == "mergesort":
            data, progress, task_dict = mergesort_partial(data, progress, time_limit, task_dict)
        elif algorithm == "heapsort":
            data, progress, task_dict = heapsort_partial(data, progress, time_limit, task_dict)

        if progress >= len(data):
            return data, progress, task_dict, True

    return data, progress, task_dict, False


def delegate_to_worker1(data, progress, algorithm, time_limit, task_dict):
    """
    Delegar la tarea a Worker 1.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker1_conn:
        try:
            worker1_conn.connect((CONFIG_PARAMS['HOST_WORKER_1'], CONFIG_PARAMS['PORT_WORKER_1']))
            send_large_data(worker1_conn, {
                "data": data,
                "progress": progress,
                "algorithm": algorithm,
                "time_limit": time_limit,
                "task_dict": task_dict
            })
            return recv_large_data(worker1_conn)
        except Exception as e:
            print(f"[Worker 0] Error al comunicarse con Worker 1: {e}")
            return None


def worker0_program():
    print("[Worker 0] Iniciado y esperando conexiones...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((CONFIG_PARAMS['HOST_WORKER_0'], CONFIG_PARAMS['PORT_WORKER_0']))
        server.listen()
        conn_client, addr = server.accept()
        print(f"[Worker 0] Nueva conexión aceptada de {addr}.")

        task = recv_large_data(conn_client)
        if not task:
            print("[Worker 0] No se recibió tarea. Finalizando.")
            conn_client.close()
            return

        algorithm = task.get("algorithm")
        data = task.get("data")
        progress = task.get("progress", 0)
        time_limit = task.get("time_limit")
        task_dict = {"estado": True}

        max_retries = 20  # Máximo de reintentos entre Worker 0 y Worker 1
        retry_count = 0
        while retry_count < max_retries:
            print(f"[Worker 0] Intento #{retry_count + 1} de procesar la tarea.")
            # Intento local en Worker 0
            data, progress, task_dict, completed = process_task(data, progress, algorithm, time_limit, task_dict)

            if completed:
                print("[Worker 0] Trabajo completado exitosamente.")
                send_large_data(conn_client, {"vector": data, "time": time.time(), "worker_id": 0})
                conn_client.close()
                return

            print("[Worker 0] No lo completó en el tiempo indicado. Delegando a Worker 1...")
            response = delegate_to_worker1(data, progress, algorithm, time_limit, task_dict)

            if response and response.get("completed"):
                print("[Worker 0] Worker 1 completó el trabajo.")
                send_large_data(conn_client, {"vector": response["data"], "time": response["time_taken"], "worker_id": response["worker"]})
                conn_client.close()
                return
            elif response:
                print("[Worker 0] Worker 1 no completó el trabajo. Reintentando localmente...")
                data = response.get("data", data)
                progress = response.get("progress", progress)
            else:
                print("[Worker 0] No se recibió respuesta válida de Worker 1. Reintentando localmente...")

            retry_count += 1

        print("[Worker 0] Se alcanzó el máximo de reintentos. Tarea no completada.")
        conn_client.close()


if __name__ == "__main__":
    worker0_program()
