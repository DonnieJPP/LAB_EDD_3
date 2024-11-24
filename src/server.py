import socket
import json
from config import CONFIG_PARAMS

def handle_client(client_socket):
    try:
        data = recv_large_data(client_socket)
        if data:
            algorithm = data.get('algorithm')
            time_limit = data.get('time_limit')
            vector = data.get('vector')

            print(f"[Servidor] Datos recibidos: algoritmo={algorithm}, tiempo límite={time_limit}, vector (primeros 10 elementos)={vector[:10]}")

            # Enviar tarea al primer worker
            worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            worker_socket.connect((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['WORKER_0_PORT']))
            send_large_data(worker_socket, data)

            # Recibir respuesta del worker
            response = recv_large_data(worker_socket)
            worker_socket.close()

            # Enviar respuesta al cliente
            send_large_data(client_socket, response)
    except Exception as e:
        print(f"[Servidor] Error: {e}")
    finally:
        client_socket.close()

def recv_large_data(socket):
    buffer = b""
    while True:
        chunk = socket.recv(8192)
        if not chunk:
            print("[Servidor] Conexión cerrada inesperadamente.")
            return None
        buffer += chunk
        if b'__END__' in buffer:
            buffer = buffer.split(b'__END__')[0]
            break

    try:
        return json.loads(buffer.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"[Servidor] Error al decodificar JSON: {e}")
        print(f"[Servidor] Datos recibidos: {buffer}")
        return None

def send_large_data(socket, data):
    try:
        serialized_data = json.dumps(data).encode('utf-8')
        socket.sendall(serialized_data + b'__END__')
    except Exception as e:
        print(f"[Servidor] Error al enviar datos: {e}")

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((CONFIG_PARAMS['SERVER_IP_ADDRESS'], CONFIG_PARAMS['SERVER_PORT']))
    server_socket.listen(5)
    print("[Servidor] Esperando conexiones...")

    # Esperar conexiones de los workers
    worker_sockets = []
    for i in range(CONFIG_PARAMS['SERVER_MAX_WORKERS']):
        worker_socket, addr = server_socket.accept()
        print(f"[Servidor] Conexión aceptada de Worker {i} en {addr}")
        worker_sockets.append(worker_socket)

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[Servidor] Conexión aceptada de {addr}")
        handle_client(client_socket)

if __name__ == '__main__':
    server()