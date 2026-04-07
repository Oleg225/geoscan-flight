n_max=int(input("Ввести максимально задуманное число: "))
var=set(range(1,n_max+1))
while True:
    predpol=input("Предположим что это числа: ")
    if predpol=="HELP":
        break
    q_set=set(map(int, predpol.split()))
    answer=input("Наш ответ Yes or No: ")
    if answer=="Yes":
        var &= q_set
    elif answer=="No":
        var -= q_set

print("Возможные загаданные числа:", *sorted(var))


