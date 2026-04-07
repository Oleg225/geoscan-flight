s = input("Введите строку:")

D = {}
for ch in s:
    D[ch] = D.get(ch, 0) + 1

for k in sorted(D):
    print(k, D[k])
    