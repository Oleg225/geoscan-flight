from tkinter import *

def toggle_text():
    if button['text'] == 'Спрятать':
        
        label.config(text="")
        button.config(text='Показать')
    else:
       
        label.config(text="Видно")
        button.config(text='Спрятать')

root = Tk()
root.geometry('300x150')


label = Label(root, text='Видно', font=('Arial', 20))
label.pack(pady=20)

button = Button(root, text='Спрятать', command=toggle_text,
                font=('Arial', 12), bg='lightgray')
button.pack(pady=10)

root.mainloop()