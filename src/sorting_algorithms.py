import time
import threading

stop_flag = threading.Event()

def merge_sort(arr, start_time, time_limit):
    if len(arr) > 1:
        if stop_flag.is_set():  # Verifica si debe detenerse
            return
        
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        # Llamadas recursivas con verificación de stop_flag
        merge_sort(left_half, start_time, time_limit)
        if stop_flag.is_set():  # Verifica si el flag se activó durante la llamada recursiva
            return
        merge_sort(right_half, start_time, time_limit)
        if stop_flag.is_set():  # Verifica nuevamente después de la segunda llamada recursiva
            return

        i = j = k = 0
        while i < len(left_half) and j < len(right_half):
            if stop_flag.is_set():  # Verifica si debe detenerse
                return
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

def quick_sort_helper(arr,low, high):
   pivot = arr[high]
   i = low - 1
   for j in range(low, high):
      if arr[j] <= pivot:
         i = i + 1
         arr[i], arr[j] = arr[j], arr[i]
   arr[i + 1], arr[high] = arr[high], arr[i + 1]
   return (i + 1)

def quick_sort(arr,low,high):
   if(low < high):
      pi = quick_sort_helper(arr, low, high)
      quick_sort(arr, low, pi - 1)
      quick_sort(arr, pi + 1, high)
