f = {1: 1, 2: 1}

for n in range(3, 41):
    f[n] = f[n - 1] + f[n - 2]

for n in sorted(f):
    print(f[n])
