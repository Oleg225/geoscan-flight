r1=set()
max_n=1000000
for x in range(max_n):
    if x % 53==17 and x % 69 == 1 and x % 65 ==5:
        r1.add(x)
for x in sorted(r1):
    print(x)