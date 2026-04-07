import random
import timeit

numbers = [random.randint(0, 1000) for _ in range(5000)]
numbers_copy = numbers.copy()

print("=" * 60)
print("ПУЗЫРЬКОВАЯ СОРТИРОВКА (Bubble Sort)")
print(f"Количество элементов: {len(numbers)}")
print("=" * 60)

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

print("Начало сортировки...")
start = timeit.default_timer()

sorted_numbers = bubble_sort(numbers_copy)

end = timeit.default_timer()
time_taken = end - start

print(f"\nСортировка завершена за {time_taken:.6f} секунд")

def check_sorted(arr):
    for i in range(1, len(arr)):
        if arr[i] < arr[i - 1]:
            return False
    return True

is_correct = check_sorted(sorted_numbers)
print(f"Проверка сортировки: {'ПРОЙДЕНА ' if is_correct else 'НЕ ПРОЙДЕНА ✗'}")

print("\nПервые 10 элементов после сортировки:")
print(sorted_numbers[:10])
print("\nПоследние 10 элементов после сортировки:")
print(sorted_numbers[-10:])

print("\n" + "=" * 60)
