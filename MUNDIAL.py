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
        conexion.close(
