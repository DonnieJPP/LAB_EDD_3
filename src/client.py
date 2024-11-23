import socket
import json
import os
from config import CONFIG_PARAMS



def load_vector_from_file(file_path):
    """Carga el vector desde un archivo de texto."""
    try:
        with open(file_path, 'r') as file:
            vector = [int(line.strip()) for line in file]
        return vector
    except FileNotFoundError:
        print(f"Error: el archivo '{file_path}' no se encontró.")
        return []
    except ValueError:
        print(f"Error: el archivo '{file_path}' contiene datos no válidos.")
        return []
    except Exception as e:
        print(f"Error al leer el archivo '{file_path}': {e}")
        return []


def client():
    import socket
    import json
    from config import CONFIG_PARAMS

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

            # Pedir detalles del problema
            print("1. Mergesort\n2. Heapsort\n3. Quicksort")
            algorithm_choice = input("Seleccione algoritmo (1-3): ")
            if algorithm_choice not in {"1", "2", "3"}:
                print("Opción inválida. Intente de nuevo.")
                continue
            algorithm = {"1": "mergesort", "2": "heapsort", "3": "quicksort"}[algorithm_choice]

            # Crear la ruta al archivo `ejemplo.txt`
            current_dir = os.path.dirname(__file__)  # Directorio donde está este script
            file_path = os.path.join(current_dir, "data", "ejemplo.txt")
            vector = load_vector_from_file(file_path)
            if not vector:
                print("Error al cargar el archivo 'ejemplo.txt'. Verifique su contenido o existencia.")
                continue

            t = int(input("Tiempo por worker (en segundos): "))

            task = {"algorithm": algorithm, "time": t, "vector": vector}
            print("[Cliente] Enviando datos al servidor...")
            client_socket.sendall(json.dumps(task).encode('utf-8'))

            result = client_socket.recv(4096)
            result_data = json.loads(result.decode('utf-8'))
            print(f"[Cliente] Vector ordenado (primeros 100 elementos): {result_data['vector'][:100]}")
            print(f"[Cliente] Tiempo total empleado: {result_data['time']} segundos")

    except Exception as e:
        print("[Cliente] Error:", e)
    finally:
        client_socket.close()


if __name__ == '__main__':
    client()
