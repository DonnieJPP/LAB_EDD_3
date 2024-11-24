import time

def merge_sort(arr, start_time, time_limit):
    if time.time() - start_time > time_limit:
        return
    if len(arr) > 1:
        mid = len(arr) // 2
        L = arr[:mid]
        R = arr[mid:]

        merge_sort(L, start_time, time_limit)
        merge_sort(R, start_time, time_limit)

        i = j = k = 0

        while i < len(L) and j < len(R):
            if time.time() - start_time > time_limit:
                return
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            if time.time() - start_time > time_limit:
                return
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            if time.time() - start_time > time_limit:
                return
            arr[k] = R[j]
            j += 1
            k += 1

def heap_sort(arr, start_time, time_limit):
    def heapify(arr, n, i):
        if time.time() - start_time > time_limit:
            return
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and arr[i] < arr[l]:
            largest = l

        if r < n and arr[largest] < arr[r]:
            largest = r

        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)

    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        if time.time() - start_time > time_limit:
            return
        heapify(arr, n, i)

    for i in range(n-1, 0, -1):
        if time.time() - start_time > time_limit:
            return
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)

def quick_sort(arr, start_time, time_limit):
    if time.time() - start_time > time_limit:
        return arr
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left, start_time, time_limit) + middle + quick_sort(right, start_time, time_limit)