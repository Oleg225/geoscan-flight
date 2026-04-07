from tkinter import *
import math

def change_color_left(new_color):
    canvas.itemconfig(left_half, fill=new_color)

def change_color_right(new_color):
    canvas.itemconfig(right_half, fill=new_color)

root = Tk()
root.geometry('300x350')  

canvas = Canvas(root, width=200, height=200, bg='white')
canvas.pack(pady=10)


left_half = canvas.create_arc(50, 50, 150, 150, 
                              start=90, extent=180, 
                              fill='white', outline='purple', width=2)

#
right_half = canvas.create_arc(50, 50, 150, 150, 
                               start=-90, extent=180, 
                               fill='white', outline='purple', width=2)

frame_top = Frame(root)
frame_top.pack()

frame_bottom = Frame(root)
frame_bottom.pack()


btn_red_left = Button(frame_top, text='Красный (лево)', bg='red',
                      command=lambda: change_color_left('red'))
btn_yellow_left = Button(frame_top, text='Желтый (лево)', bg='yellow',
                         command=lambda: change_color_left('yellow'))
btn_green_left = Button(frame_top, text='Зеленый (лево)', bg='green',
                        command=lambda: change_color_left('green'))

btn_red_left.pack(side=LEFT, padx=5, pady=5)
btn_yellow_left.pack(side=LEFT, padx=5, pady=5)
btn_green_left.pack(side=LEFT, padx=5, pady=5)

btn_red_right = Button(frame_bottom, text='Красный (право)', bg='red',
                       command=lambda: change_color_right('red'))
btn_yellow_right = Button(frame_bottom, text='Желтый (право)', bg='yellow',
                          command=lambda: change_color_right('yellow'))
btn_green_right = Button(frame_bottom, text='Зеленый (право)', bg='green',
                         command=lambda: change_color_right('green'))

btn_red_right.pack(side=LEFT, padx=5, pady=5)
btn_yellow_right.pack(side=LEFT, padx=5, pady=5)
btn_green_right.pack(side=LEFT, padx=5, pady=5)

root.mainloop()