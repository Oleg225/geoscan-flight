r=set()
n_max=200
s=set()

for x in range(1, n_max):
    for y in range(1, n_max):
        num=15*x+23*y
        if num <=n_max:
            s.add(num)
for num in s:
    if num % 16==0:
        r.add(num)
print(sorted(r))
