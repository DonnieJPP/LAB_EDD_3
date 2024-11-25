import time
def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

def heapify(arr, n, i):
    
    largest = i  # Inicializar el nodo raíz como el más grande
    left = 2 * i + 1  # Índice del hijo izquierdo
    right = 2 * i + 2  # Índice del hijo derecho

    # Comparar el hijo izquierdo con el nodo raíz
    if left < n and arr[left] > arr[largest]:
        largest = left

    # Comparar el hijo derecho con el nodo más grande actual
    if right < n and arr[right] > arr[largest]:
        largest = right

    # Si el nodo raíz no es el más grande, intercambiar y continuar
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # Intercambiar
        heapify(arr, n, largest)  # Llamar recursivamente

def heap_sort(arr):
    
    n = len(arr)

    # Construir el heap máximo
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # Extraer elementos del heap uno por uno
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # Mover la raíz al final
        heapify(arr, i, 0)  # Llamar heapify para el subárbol reducido


def quick_sort_worker(arr, time_limit, task_dict, worker_id):
    start_time = time.time()
    stack = task_dict.get("stack", [(0, len(arr) - 1)])
    
    while stack:
        low, high = stack.pop()
        if low < high:
            p = partition(arr, low, high)
            stack.append((low, p - 1))
            stack.append((p + 1, high))
        
        # Verificar si se ha alcanzado el tiempo límite
        if time.time() - start_time >= time_limit:
            print(f"Worker {worker_id} no alcanzó el tiempo límite")
            task_dict["estado"] = False  # Indicar que no se completó
            task_dict["progress"] = get_sorting_progress(arr)
            task_dict["stack"] = stack
            return arr, task_dict

    print(f"Worker {worker_id} completó el ordenamiento dentro del tiempo")
    task_dict["estado"] = True  # El trabajo está completo
    return arr, task_dict

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def get_sorting_progress(arr):
    # Función para calcular el progreso del ordenamiento
    return sum(1 for i in range(1, len(arr)) if arr[i-1] <= arr[i]) / len(arr)

def continue_sorting(arr, task_dict, worker_id):
    stack = task_dict.get("stack", [])
    while stack:
        low, high = stack.pop()
        if low < high:
            p = partition(arr, low, high)
            stack.append((low, p - 1))
            stack.append((p + 1, high))
    print(f"Worker {worker_id} completó el ordenamiento continuando desde el progreso anterior")
    task_dict["estado"] = True
    return arr, task_dict

# Lógica para alternar entre los workers
def alternate_workers(arr, time_limit):
    task_dict = {"estado": False, "progress": 0, "stack": []}
    workers = [0, 1]
    current_worker = 0
    
    while not task_dict["estado"]:
        arr, task_dict = quick_sort_worker(arr, time_limit, task_dict, worker_id=workers[current_worker])
        current_worker = (current_worker + 1) % 2  # Alternar entre 0 y 1
    
    return arr, task_dict
def tiempo_ejecución(ordenamiento,vector, t):
    vectorB = vector.copy()
    inicio = time.time()
    while tiempo<=t:
     tiempo_actual = time.time()
     tiempo = tiempo_actual - inicio
     ordenamiento(vectorB)
