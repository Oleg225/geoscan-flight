s1 = input("Введите 1 строку: ")
s2 = input("Введите 2 строку: ")
s3 = input("Введите 3 строку: ")

set1=set(s1)
set2=set(s2)
set3=set(s3)

a=set1 & set2 & set3
print("Символы входящие во все множества:",a)

b=set1 | set2 | set3
print("Символы входящие в 1 строку:",b)

only1=set1 - set2 - set3
only2=set2 - set1 - set3
only3=set3 - set2 - set1
print("Символы только в 1 строке:",only1)
print("Символы только в 2 строке:",only2)
print("Символы только в 3 строке:",only3)

