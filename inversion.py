import random
import timeit

numbers = [random.randint(0, 1000) for _ in range(5000)]
numbers1 = numbers.copy()
numbers2 = numbers.copy()
numbers3 = numbers.copy()

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def counting_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    min_val = min(arr)
    count_size = max_val - min_val + 1
    count = [0] * count_size
    for num in arr:
        count[num - min_val] += 1
    result = []
    for i in range(count_size):
        result.extend([i + min_val] * count[i])
    return result

print("Пузырьковая сортировка:")
start = timeit.default_timer()
bubble_sort(numbers1)
end = timeit.default_timer()
print(f"Время: {end - start:.6f} сек")

print("\nСортировка вставками:")
start = timeit.default_timer()
insertion_sort(numbers2)
end = timeit.default_timer()
print(f"Время: {end - start:.6f} сек")

print("\nСортировка подсчетом:")
start = timeit.default_timer()
result = counting_sort(numbers3)
end = timeit.default_timer()
print(f"Время: {end - start:.6f} сек")