import time

def quicksort_partial(arr, progress, high, time_limit, task_dict):
    start_time = time.time()
    stack = [(progress, high)]

    while stack:
        low, high = stack.pop()
        if low < high:
            p = partition(arr, low, high)
            stack.append((low, p - 1))
            stack.append((p + 1, high))

        if time.time() - start_time >= time_limit:
            print("[Quicksort] No alcanzó el tiempo límite.")
            task_dict["estado"] = False
            return arr, progress, task_dict

    print("[Quicksort] Ordenamiento completado dentro del tiempo.")
    task_dict["estado"] = True
    return arr, len(arr), task_dict


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def mergesort_partial(arr, progress, time_limit, task_dict):

    start_time = time.time()
    n = len(arr)
    width = 1

    # Recupera la anchura actual y el índice basado en el progreso
    if "width" in task_dict:
        width = task_dict["width"]
    if progress > 0:
        while width < progress and width < n:
            width *= 2

    while width < n:
        for i in range(progress, n, 2 * width):
            left = arr[i:i + width]
            right = arr[i + width:i + 2 * width]
            arr[i:i + 2 * width] = merge(left, right)
            
            # Actualiza el progreso después de procesar esta sección
            progress = i + 2 * width

            # Verifica si se alcanzó el tiempo límite
            if time.time() - start_time >= time_limit:
                print("[Mergesort] Tiempo límite alcanzado.")
                task_dict["estado"] = False
                task_dict["width"] = width  # Guarda el nivel actual de anchura
                return arr, progress, task_dict
        
        # Incrementa el nivel de anchura
        width *= 2
        progress = 0  # Reinicia el índice al comienzo para la nueva anchura

    print("[Mergesort] Ordenamiento completado.")
    task_dict["estado"] = True
    task_dict.pop("width", None)  # Limpia el nivel de anchura al finalizar
    return arr, len(arr), task_dict


def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heapsort_partial(arr, progress, time_limit, task_dict):
    start_time = time.time()
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
        if time.time() - start_time >= time_limit:
            print("[Heapsort] No alcanzó el tiempo límite.")
            task_dict["estado"] = False
            return arr, progress, task_dict

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
        progress += 1
        if time.time() - start_time >= time_limit:
            print("[Heapsort] No alcanzó el tiempo límite.")
            task_dict["estado"] = False
            return arr, progress, task_dict

    print("[Heapsort] Ordenamiento completado dentro del tiempo.")
    task_dict["estado"] = True
    return arr, len(arr), task_dict


def heapify(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] > arr[largest]:
        largest = left

    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)