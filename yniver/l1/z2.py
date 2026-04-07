a = list(map(int, input("Введите 5 чисел через пробел:").split()))

D = {}
for x in a:
    D[x] = D.get(x, 0) + 1

v = sorted(D.values())

if v == [5]:
    print("poker")
elif v == [1, 4]:
    print("four of a kind")
elif v == [2, 3]:
    print("full house")
elif v == [1, 1, 3]:
    print("three of a kind")
elif v == [1, 2, 2]:
    print("two pairs")
elif v == [1, 1, 1, 2]:
    print("one pair")
else:
    print("all different")
