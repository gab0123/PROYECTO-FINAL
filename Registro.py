import os
import sys
import time
import sqlite3

def menu_Continentes():
    op = "0"
    listCont = ["Africa","Asia","Europa","N/Centro America y Caribe","Oceania","Sudamerica"]
    while(op == "0"):
        print("\n\tCONTIENENTES")
        print(" 1.- {}\n 2.- {}\n 3.- {}\n 4.- {}\n 5.- {}\n 6.- {}".format(listCont[0],listCont[1],listCont[2],listCont[3],listCont[4],listCont[5]))
        op = str(input("\nIngrese un opcion: "))
        if op not in ["1","2","3","4","5","6"]:
            print("Opcion incorrecta, Vuelva a intentarlo!")
            time.sleep(2)
            op = "0"
        os.system("cls")
    aux = int(op)-1
    cont = listCont[aux]
    return cont


       
                  
               
