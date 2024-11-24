import socket
import json
from pathlib import Path
from config import CONFIG_PARAMS

def load_vector_from_file(file_path):
    """Carga el vector desde un archivo de texto donde cada número está en una línea."""
    try:
        file_path = Path(file_path).resolve(strict=True)
        with file_path.open('r') as file:
            vector = [int(line.strip()) for line in file]
        return vector
    except Exception as e:
        print(f"[Cliente] Error al cargar el archivo '{file_path}': {e}")
        return []
    
def send_large_data(socket, data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
        socket.sendall(serialized_data + b'__END__')
    except Exception as e:
        print(f"[Cliente] Error al enviar datos: {e}")

def recv_large_data(socket):
    buffer = b""
    while True:
        chunk = socket.recv(8192)
        if not chunk:  # Verifica si la conexión se cerró abruptamente
            print("[Cliente] Conexión cerrada inesperadamente.")
            return None  # Manejo de error
        if b'__END__' in chunk:
            buffer += chunk.replace(b'__END__', b'')
            break
        buffer += chunk

    try:
        return json.loads(buffer.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"[Cliente] Error al decodificar JSON: {e}")
        print(f"[Cliente] Datos recibidos: {buffer}")
        return None

def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_0_PORT']))
    client_socket.settimeout(30)

    try:
        while True:
            print("\n--- MENÚ ---")
            print("1. Seleccionar algoritmo de ordenamiento")
            print("2. Salir")
            choice = input("Seleccione una opción: ")

            if choice == "2":
                print("[Cliente] Finalizando cliente.")
                break

            print("\nAlgoritmos disponibles:")
            print("1. MergeSort")
            print("2. HeapSort")
            print("3. QuickSort")
            algorithm_choice = input("Seleccione un algoritmo (1-3): ")
            algorithm = {"1": "mergesort", "2": "heapsort", "3": "quicksort"}.get(algorithm_choice)

            if not algorithm:
                print("[Cliente] Opción inválida.")
                continue

            file_path = Path(__file__).parent / "data" / "ejemplo.txt"
            vector = load_vector_from_file(file_path)
            if not vector:
                print("[Cliente] Error al cargar el archivo 'ejemplo.txt'. Verifique su contenido o existencia.")
                continue

            if not vector:
                continue

            try:
                time_limit = float(input("Ingrese el tiempo límite por worker (en segundos): "))
            except ValueError:
                print("[Cliente] Tiempo inválido. Intente de nuevo.")
                continue

            task = {"algorithm": algorithm, "time_limit": time_limit, "vector": vector}
            print("[Cliente] Enviando tarea a Worker 0...")
            send_large_data(client_socket, task)

            response = client_socket.recv(9192)
            result = json.loads(response.decode('utf-8'))
            print(f"\n[Cliente] Vector ordenado (primeros 10 elementos): {result['vector'][:10]}")
            print(f"[Cliente] Tiempo total: {result['time']} segundos")
            print(f"[Cliente] Worker que completó: Worker {result['worker_id']}")

    except Exception as e:
        print(f"[Cliente] Error: {e}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    client()
