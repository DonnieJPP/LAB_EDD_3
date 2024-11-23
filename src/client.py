import socket
import json
import random
from config import CONFIG_PARAMS

def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['SERVER_PORT']))

    try:
        # Elegir algoritmo
        print("1. Mergesort\n2. Heapsort\n3. Quicksort")
        choice = input("Seleccione algoritmo (1-3): ")
        algorithm = {"1": "mergesort", "2": "heapsort", "3": "quicksort"}[choice]

        # Configurar tiempo y vector
        t = int(input("Tiempo por worker (segundos): "))
        n = int(input("Tamaño del vector: "))
        vector = [random.randint(0, 1000000) for _ in range(n)]

        # Enviar datos
        task = json.dumps({"algorithm": algorithm, "time": t, "vector": vector})
        client_socket.sendall(task.encode('utf-8'))

        # Recibir resultado
        result = client_socket.recv(2048)
        print("Resultado:", result.decode('utf-8'))

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == '__main__':
    client()
