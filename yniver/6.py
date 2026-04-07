N, K =map(int, input().split())
Zabostovka = set()

for x in range(K):
    a,b =map(int, input().split())
    day = a
    while day <= N:
        Zabostovka.add(a)
        day+=b
c=0
for day in Zabostovka:
    if  day %7 !=0 or  day%7 !=1:
        c+=1
print(c)
