from pathlib import Path
import socket
import json
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

def send_large_data(sock, data):
    """Envía datos grandes en partes."""
    serialized = json.dumps(data)
    sock.sendall(serialized.encode('utf-8'))

def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['SERVER_PORT']))

    try:
        while True:
            print("\nOpciones:")
            print("1. Resolver problema")
            print("2. Salir")
            choice = input("Seleccione una opción (1-2): ")

            if choice == "2":
                client_socket.sendall(CONFIG_PARAMS['EXIT_MESSAGE'].encode('utf-8'))
                print("[Cliente] Saliendo.")
                break

            print("\nAlgoritmos disponibles:")
            print("1. Mergesort")
            print("2. Heapsort")
            print("3. Quicksort")
            algorithm_choice = input("Seleccione algoritmo (1-3): ")
            if algorithm_choice not in {"1", "2", "3"}:
                print("[Cliente] Opción inválida. Intente de nuevo.")
                continue
            algorithm = {"1": "mergesort", "2": "heapsort", "3": "quicksort"}[algorithm_choice]

            file_path = Path(__file__).parent / "data" / "ejemplo.txt"
            vector = load_vector_from_file(file_path)
            if not vector:
                print("[Cliente] Error al cargar el archivo 'ejemplo.txt'. Verifique su contenido o existencia.")
                continue

            try:
                t = int(input("Tiempo por worker (en segundos): "))
                if t <= 0:
                    print("[Cliente] El tiempo debe ser un número positivo.")
                    continue
            except ValueError:
                print("[Cliente] Debe ingresar un número válido para el tiempo.")
                continue

            task = {"algorithm": algorithm, "time": t, "vector": vector}
            print("[Cliente] Enviando datos al servidor...")
            send_large_data(client_socket, task)

            result = b""
            while True:
                part = client_socket.recv(4096)
                if not part:
                    break
                result += part
            result_data = json.loads(result.decode('utf-8'))
            print(f"\n[Cliente] Vector ordenado (primeros 100 elementos): {result_data['vector'][:100]}")
            print(f"[Cliente] Tiempo total empleado: {result_data['time']} segundos")

    except Exception as e:
        print("[Cliente] Error:", e)
    finally:
        client_socket.close()

if __name__ == '__main__':
    client()
