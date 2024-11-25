
import socket
import json
from pathlib import Path
from config import CONFIG_PARAMS


def load_vector_from_file(file_path):
    try:
        file_path = Path(file_path).resolve(strict=True)
        with file_path.open('r') as file:
            vector = [float(line.strip()) for line in file if line.strip().isdigit()]
        return vector
    except FileNotFoundError:
        print(f"[Cliente] Error: El archivo '{file_path}' no existe.")
        return []
    except ValueError as e:
        print(f"[Cliente] Error al leer el archivo: {e}")
        return []


def send_large_data(socket, data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
        socket.sendall(serialized_data + b'__END__')
    except Exception as e:
        print(f"[Cliente] Error al enviar datos: {e}")


def recv_large_data(socket):
    buffer = b""
    try:
        while True:
            chunk = socket.recv(8192)
            if not chunk:
                print("[Cliente] Conexión cerrada inesperadamente.")
                return None
            buffer += chunk
            if b'__END__' in buffer:
                buffer = buffer.split(b'__END__')[0]
                break
        return json.loads(buffer.decode('utf-8'))
    except (ConnectionResetError, json.JSONDecodeError) as e:
        print(f"[Cliente] Error al recibir datos: {e}")
        return None


def client_program():
    print("[Cliente] Iniciando cliente...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((CONFIG_PARAMS['HOST_WORKER_0'], CONFIG_PARAMS['PORT_WORKER_0']))
        print("[Cliente] Conectado exitosamente a Worker 0.")

        print("\n--- MENÚ ---")
        print("1. MergeSort")
        print("2. HeapSort")
        print("3. QuickSort")
        algorithm_choice = input("Seleccione un algoritmo (1-3): ")
        algorithm = {"1": "mergesort", "2": "heapsort", "3": "quicksort"}.get(algorithm_choice)

        if not algorithm:
            print("[Cliente] Opción inválida.")
            return

        file_path = Path(__file__).parent / "data" / "ejemplo.txt"
        vector = load_vector_from_file(file_path)
        if not vector:
            print("[Cliente] Error al cargar el archivo.")
            return

        try:
            time_limit = float(input("Ingrese el tiempo límite por worker (en segundos): "))
        except ValueError:
            print("[Cliente] Tiempo inválido. Intente de nuevo.")
            return

        task = {"algorithm": algorithm, "time_limit": time_limit, "data": vector, "progress": 0}
        send_large_data(client_socket, task)
        print("[Cliente] Enviando tarea a Worker 0...")

        response = recv_large_data(client_socket)
        if response is None:
            print("[Cliente] No se recibió respuesta del servidor.")
        else:
            print(f"\n[Cliente] Vector ordenado (primeros 1000 elementos): {response['vector'][:1000]}")
            print(f"[Cliente] Tiempo total: {response['time']} segundos")
            print(f"[Cliente] Worker que completó: Worker {response['worker_id']}")

    except Exception as e:
        print(f"[Cliente] Error: {e}")
    finally:
        print("[Cliente] Cerrando la conexión.")
        client_socket.close()


if __name__ == '__main__':
    client_program()
