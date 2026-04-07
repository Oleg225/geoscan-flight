A = {
    'Андреев': 5,
    'Петров': 3,
    'Сергеев': 2,
    'Иванов': 4,
    'Сидоров': 2
}

B = {
    'Сергеев': 4,
    'Сидоров': 3,
    'Кузнецов': 5,
    'Орлов': 3
}


print("Пересдавали двойку:")
for name in B:
    if A.get(name) == 2:
        print(name)

print("Только пересдача:")
for name in B:
    if name not in A:
        print(name)
