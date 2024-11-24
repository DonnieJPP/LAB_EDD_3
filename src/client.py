import socket
import json
from config import CONFIG_PARAMS

def load_vector_from_file(filename):
    try:
        print(f"[Cliente] Intentando leer archivo: {filename}")
        with open(filename, 'r') as file:
            vector = [int(line.strip()) for line in file]
            print(f"[Cliente] Vector leído exitosamente. Tamaño: {len(vector)}")
            return vector
    except FileNotFoundError:
        print(f"[Cliente] Error: El archivo {filename} no existe")
        return None
    except Exception as e:
        print(f"[Cliente] Error al leer archivo: {e}")
        return None

def client():
    try:
        print("[Cliente] Iniciando conexión con el servidor...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['SERVER_PORT']))
        
        # Identificarse con el servidor
        sock.send("client".encode())
        print("[Cliente] Conectado exitosamente al servidor")
        
        while True:
            print("\n=== Menú de Ordenamiento ===")
            print("1. Ordenar vector")
            print("2. Salir")
            choice = input("Seleccione una opción: ")
            
            if choice == "2":
                print("[Cliente] Enviando solicitud de salida")
                sock.send(json.dumps({'command': CONFIG_PARAMS['EXIT_MESSAGE']}).encode())
                break
                
            if choice == "1":
                # Selección de algoritmo
                print("\nAlgoritmos disponibles:")
                print("1. Mergesort")
                print("2. Heapsort")
                print("3. Quicksort")
                alg_choice = input("Seleccione algoritmo (1-3): ")
                
                algorithm = {
                    "1": "mergesort",
                    "2": "heapsort",
                    "3": "quicksort"
                }.get(alg_choice)
                
                if not algorithm:
                    print("[Cliente] Error: Algoritmo inválido")
                    continue
                
                # Solicitar archivo
                filename = input("Ingrese la ruta del archivo con el vector: ")
                vector = load_vector_from_file(filename)
                if not vector:
                    continue
                
                # Tiempo límite
                try:
                    time_limit = float(input("Tiempo límite por worker (segundos): "))
                    if time_limit <= 0:
                        print("[Cliente] Error: El tiempo debe ser mayor a 0")
                        continue
                except ValueError:
                    print("[Cliente] Error: Tiempo inválido")
                    continue
                
                # Preparar y enviar tarea
                task = {
                    'algorithm': algorithm,
                    'vector': vector,
                    'time_limit': time_limit
                }
                
                print("\n[Cliente] Enviando tarea al servidor")
                print(f"[Cliente] - Algoritmo: {algorithm}")
                print(f"[Cliente] - Tamaño del vector: {len(vector)}")
                print(f"[Cliente] - Tiempo límite por worker: {time_limit}s")
                
                sock.send(json.dumps(task).encode())
                print("[Cliente] Esperando resultado...")
                
                # Recibir y mostrar resultado
                result = json.loads(sock.recv(4096).decode())
                if 'error' in result:
                    print(f"[Cliente] Error recibido: {result['error']}")
                else:
                    print("\n=== Resultado del Ordenamiento ===")
                    print(f"Primeros 10 elementos ordenados: {result['vector'][:100]}")
                    print(f"Últimos 10 elementos ordenados: {result['vector'][-100:]}")
                    print(f"Tiempo total de procesamiento: {result['time_used']:.2f} segundos")
                    print(f"Completado por: Worker {result['completed_by']}")
    
    except ConnectionRefusedError:
        print("[Cliente] Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"[Cliente] Error inesperado: {e}")
    finally:
        print("[Cliente] Cerrando conexión")
        sock.close()