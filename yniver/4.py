a = list(map(int, input("Введите числа через пробел:").split()))
m=set()
for x in a:
    if x in m:
        print("YES")
    else:
        print("NO")
        m.add(x)
