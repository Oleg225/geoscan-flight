m = 200
for x in range(100):
    m -= m / 100 + 1
print(m)
