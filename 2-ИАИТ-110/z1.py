a=input("Введите строку c символами: ")
s={}
for x in a:
    s[x]=s.get(x, 0) + 1
for x in sorted(s):
    print(x, "всего:", s[x])


