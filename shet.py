import random
import timeit


numbers = [random.randint(0, 1000) for _ in range(5000)]
numbers_copy = numbers.copy()

print("=" * 60)
print("СОРТИРОВКА ПОДСЧЕТОМ (Counting Sort)")
print(f"Количество элементов: {len(numbers)}")
print("=" * 60)


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

print("Начало сортировки...")
start = timeit.default_timer()

sorted_numbers = counting_sort(numbers_copy)

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

print(f"СЛОЖНОСТЬ: O(n + k), где k = {max(numbers) - min(numbers) + 1} (диапазон значений)")
print(f"Дополнительная память: O(k) = {max(numbers) - min(numbers) + 1} элементов")
print("=" * 60)

print("\nДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:")
print(f"Минимальное значение: {min(numbers)}")
print(f"Максимальное значение: {max(numbers)}")
print(f"Диапазон значений: {max(numbers) - min(numbers) + 1}")