operations = [
    ('1', 500),
    ('2', 1000),
    ('1', -200),
    ('3', 700),
    ('2', -300),
    ('1', 150)
]

D = {}

for n, money in operations:
    D[n] = D.get(n, 0) + money

print("Итог по счетам:")
for n in sorted(D):
    print(n, D[n])
