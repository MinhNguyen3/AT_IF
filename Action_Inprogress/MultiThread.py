from threading import Thread
import time


import sys
from os.path import dirname, join, abspath
working_folder = abspath(join(dirname(__file__), '..'))
sys.path.insert(0, working_folder)  

from Actions.Log import *
import Actions.Comport as Comport
from Actions.GenerateBarcode import *
# <name_thread> = Thread(target = <function>)
# <name_thread>.start()

number = 0

def add(str1="===================",str2="*****************"):
    while True:
        global number 
        number += 1
        print(str1)
        print("Add - ",number)
        print(str2)
        time.sleep(1)

def sub():
    while True:
        global number 
        number -= 1
        print("Sub - ",number)
        time.sleep(5)


thread1 = Thread(target=ShowLabel,args=("ABCDEF","code128"))
thread2 = Thread(target=sub)

thread1.start()
thread2.start()

# if number == -5:
#     thread1.