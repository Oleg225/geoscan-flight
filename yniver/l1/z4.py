
A = {
    (1, 1): 5,
    (1, 3): 2,
    (2, 2): -1
}


B = {
    (1, 2): 4,
    (1, 3): 7,
    (2, 2): 1,
    (3, 1): 6
}

C = A.copy()

for k in B:
    C[k] = C.get(k, 0) + B[k]
    if C[k] == 0:
        del C[k]

print("Сумма матриц:")
for k in sorted(C):
    print(k, C[k])


