import os
import sys
import time
import sqlite3

class mundial:
    def __init__(self):
        self.Pais= ""
        self.Puntaje = ""
        self.Partidos_Ganados = ""
        self.Partidos_Empatados = ""
        self.Partidos_Perdidos = ""

    def grupo(self,pais1,pais2,pais3,pais4):
        os.system("cls")
        Pais = str(input("Pais: "))
        Puntaje = int(input("Puntaje: "))

        conexion = sqlite3.connect("mundial.s3db")
        cursor = conexion.cursor()
        cursor.execute("insert into mundial (Pais, Puntaje, Partidos_Ganados, Partidos_Empatados, Partidos_Perdidos  ) values ('" + Puntaje + "','"+Partidos_Ganados+"','" +Partidos_Empatados+ "','" +Partidos_Perdidos+ "')")
        conexion.commit()
        conexion.close()
        def tabla(self):
        os.system("cls")
        conexion = sqlite3.connect("mundial.s3db")
        cursor = conexion.cursor()
        cursor.execute("SELECT * from Grupos")
        print("Pais\tPuntaje\t\tPG\t\tPE\t\tPP")
        for i in cursor:
            print("{}\t\t{}\t\t{}\t\t{}\t\t{}".format(i[1],i[2],i[3],i[4],i[5]))
        conexion.commit()
        conexion.close()
