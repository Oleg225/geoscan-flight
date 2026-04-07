s = input()
while not s.isdigit():
     s = input("Введите только цифры: ")
count = [0] * 10
for ch in s:
    count[int(ch)] += 1
for i in range(10):
    print(i, ":", count[i])
