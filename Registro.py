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
    
class Registro:
    def __init__(self):
        self.continente = ""
        self.pais = ""
        self.tecnico = ""
        self.jugadores = []

    def inscripcion(self):
        os.system("cls")
        continente = menu_Continentes()
        print("\n Ingrese los siguentes Datos\nContinente: ",continente)
        pais = str(input("Pais: "))
        tecnico = str(input("Tecnico: "))

        conexion = sqlite3.connect("Registro.s3db")
        cursor = conexion.cursor()
        cursor.execute("insert into Registro (Continente, Pais, Tecnico) values ('"+continente+"','"+pais+"','"+tecnico+"')")
        conexion.commit()
        conexion.close()
        print("Se registro con exito!")

    def mostrar_Reg(self):
        os.system("cls")
        cont = menu_Continentes()
        conexion = sqlite3.connect("Registro.s3db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * from Registro")
        if(cont == "Africa"):
            for i in cursor:
                if (i[0] == "Africa"):
                    print("ID: {}".format(i[0]))
                    print("Pais: {}".format(i[2]))
                    print("Tecnico: {}".format(i[3]))
                    print("---------------")
        elif(cont == "Asia"):
            for i in cursor:
                if (i[0] == "Asia"):
                    print("ID: {}".format(i[0]))
                    print("Pais: {}".format(i[1]))
                    print("Tecnico: {}".format(i[2]))
                    print("---------------")
        elif(cont == "Europa"):
            print("\tEUROPA")
            for i in cursor:
                if (i[1] == "Europa"):
                    print("ID: {}".format(i[0]))
                    print("Pais: {}".format(i[2]))
                    print("Tecnico: {}".format(i[3]))
                    print("------------------")
        elif(cont == "N/Centro America y Caribe"):
            print("\tN/CENTRO AMERICA Y CARIBE")
            for i in cursor:
                if (i[1] == "N/Centro America y Caribe"):
                    print("ID: {}".format(i[0]))
                    print("Pais: {}".format(i[2]))
                    print("Tecnico: {}".format(i[3]))
                    print("------------------")
        elif(cont == "Oceania"):
            print("\tOCEANIA")
            for i in cursor:
                if (i[1] == "Oceania"):
                    print("ID: {}".format(i[0]))
                    print("Pais: {}".format(i[2]))
                    print("Tecnico: {}".format(i[3]))
                    print("------------------")
        elif(cont == "Sudamerica"):
            print("\tSUDAMERICA")
            for i in cursor:
                if (i[1] == "Sudamerica"):
                    print("ID: {}".format(i[0]))
                    print("Pais: {}".format(i[2]))
                    print("Tecnico: {}".format(i[3]))
                    print("------------------")
    
    
    def modificar(self):
        self.mostrar_Reg()
        codigo = str(input("Ingrese el Codigo del que desea modificar: "))
        os.system("cls")
        print("Ingresando los nuevos Datos")
        continente = menu_Continentes()
        pais = str(input("Pais: "))
        tecnico = str(input("Tecnico: "))
        conexion = sqlite3.connect("Registro.s3db")
        cursor = conexion.cursor()
        cursor.execute("update Registro set Continente = '"+continente+"', Pais = '"+pais+"', Tecnico = '"+tecnico+"' where ID = '"+codigo+"'")
        conexion.commit()
        conexion.close()
        os.system("cls")
        print("Su Modificacion se Realizo con Exito!")
        time.sleep(2)
        
def registro_Menu():
    op = 0
    r = Registro()
    listMenu = ["Inscripcion","Modificar Inscripcion","Monstrar Paises Inscritos","Eliminar Inscripcion","Atras"]
    while(op not in [1,2,3,4,5]):
        print("\n\tREGISTRO")
        print(" 1.- {}\n 2.- {}\n 3.- {}\n 4.- {}\n 5.- {}\n".format(listMenu[0],listMenu[1],listMenu[2],listMenu[3],listMenu[4]))
        op = input("Ingrese una opcion: ")
        try:
            op = int(op)
            if op not in [1,2,3,4,5,6]:
                print("Opcion incorrecta, Vuelva a intentarlo!")
                time.sleep(2)
                os.system("cls")
        except ValueError:
            print("Ingrese solo digitos!")
            time.sleep(5)
            op = 0

    if(op == 1):
        r.inscripcion()
    elif(op == 2):
        r.modificar()
    elif(op == 3):
        r.mostrar_Reg()
    elif(op == 4):
        r.eliminar()
    elif(op == 5):
        menu()
        
                  
def menu():
    op = "0"
    listMenu = ["Informacion","Registro","Equipos","Eliminatorias","Mundial","Campeon","Salir"]
    while(op == "0"):
        print("\nCOPA MUNDIAL DE LA FIFA RUSIA 2018\n")
        print(" 1.- {}\n 2.- {}\n 3.- {}\n 4.- {}\n 5.- {}\n 6.- {}\n 7.- {}".format(listMenu[0],listMenu[1],listMenu[2],listMenu[3],listMenu[4],listMenu[5],listMenu[6]))
        op = str(input("\nIngrese un opcion: "))
        if op not in ["1","2","3","4","5","6","7"]:
            print("Opcion incorrecta, Vuelva a intentarlo!")
            time.sleep(2)
            op = "0"
        os.system("cls")
    if (op == "1"):
        informacion()
    elif (op == "2"):
        registro_Menu()
