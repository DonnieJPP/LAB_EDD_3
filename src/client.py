import socket
import json
import random
from config import CONFIG_PARAMS

# Configuration Parameters
SERVER_IP_ADDRESS = CONFIG_PARAMS['SERVER_IP_ADDRESS']
SERVER_PORT = CONFIG_PARAMS['SERVER_PORT']
EXIT_MESSAGE = CONFIG_PARAMS['EXIT_MESSAGE']

def load_vector_from_file(file_path):
    """Carga el vector desde un archivo de texto"""
    try:
        with open(file_path, 'r') as file:
            vector = [int(num) for num in file.read().split()]
        return vector
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return []

def client():
    

    # Establecer conexión con worker_0
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CONFIG_PARAMS['WORKER_0_IP'], CONFIG_PARAMS['WORKER_0_PORT']))

    try:
        while True:
            print("\nOpciones:")
            print("1. Resolver problema")
            print("2. Salir")
            choice = input("Seleccione una opción (1-2): ")

            if choice == "2":
                client_socket.sendall(CONFIG_PARAMS['EXIT_MESSAGE'].encode('utf-8'))
                print("[Cliente] Mensaje de salida enviado. Cerrando conexión.")
                break

            # Resolver problema
            print("1. Mergesort\n2. Heapsort\n3. Quicksort")
            algorithm_choice = input("Seleccione algoritmo (1-3): ")
            algorithm = {"1": "mergesort", "2": "heapsort", "3": "quicksort"}[algorithm_choice]

            t = int(input("Tiempo por worker (segundos): "))
            n = int(input("Tamaño del vector: "))
            vector = [random.randint(0, 1000000) for _ in range(n)]

            task = {"algorithm": algorithm, "time": t, "vector": vector}
            print("[Cliente] Enviando datos al worker_0...")
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
