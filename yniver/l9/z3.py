from tkinter import *
from random import randint

def check_guess():

    global secret_number
    try:
        guess = int(entry.get())
        
        if guess < secret_number:
            result_label.config(text="Задуманное число больше") 
        elif guess > secret_number:
            result_label.config(text="Задуманное число меньше")
        else:
            result_label.config(text="Задуманное число угадано!")

            secret_number = randint(1, 100)
            entry.delete(0, END)
    except ValueError:
        result_label.config(text="Ошибка! Введите целое число.") 

root = Tk()
root.title('Угадай число')
root.geometry('350x200')

secret_number = randint(1, 100)

Label(root, text='Я загадал число от 1 до 100',
      font=('Arial', 12)).pack(pady=10)

entry = Entry(root, font=('Arial', 14), justify='center')
entry.pack(pady=5, ipady=5)
entry.bind('<Return>', check_guess)  

Button(root, text='Проверить', command=check_guess,
       bg='lightblue').pack(pady=5)

result_label = Label(root, text='Введите число и нажмите Enter',
                     font=('Arial', 10), fg='blue')
result_label.pack(pady=5)

root.mainloop()