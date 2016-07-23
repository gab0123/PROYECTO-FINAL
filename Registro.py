import os
import sys
import time
import sqlite3

class Registro:
    def __init__(self):
        self.continente = ""
        self.pais = ""
        self.tecnico = ""
        self.jugadores = []

    def inscripcion(self):
        os.system("cls")
        print("\n Ingrese los siguentes Datos:\n")
        continente = str(input("Continente: "))
        pais = str(input("Pais: "))
        tecnico = str(input("Tecnico: "))

        con = sqlite3.connect("Registro.s3db")
        cursor = con.cursor()
        cursor.execute("insert into Registro (Continente, Pais, Tecnico) values ('"+continente+"','"+pais+"','"+tecnico+"')")
        con.commit()
        con.close()
        print("Se registro con exito!")
