class Registro:
    def __init__(self):
        self.lista_depor = ["Futbol"," Vóley"," Básquet"," Atletismo"," Natación "]

    def inscripcion(self):
        Deporte = menu_deport()
        os.system("cls")
        print("\n Ingrese los siguentes Datos\nDeporte: {}".format(Deporte))
        Deporte = Deporte.title()
        Area = str(input("Areas: "))
        Area = Area.title()
        Escuela = str(input("Escuela profesional: "))
        Escuela = Escuela.title()
        Participante = str(input("Participante: "))
        Participante = Participante.title()
        CUI = str(input("CUI:"))
        CUI = CUI.title()

        conexion1 = sqlite3.connect(base1)
        cursor1 = conexion1.cursor()
        cursor1.execute("insert into Registro2 (Deporte,Area, Escuela, Participante, CUI) values ('"+Deporte+"','"+Area+"','"+Escuela+"','"+Participante+"','"+CUI+"')")

        conexion2 = sqlite3.connect(base2)
        cursor2 = conexion2.cursor()
        if (Deporte == self.lista_depor[0]):
            cursor2.execute("insert into futbol (Area,Escuela,Participante,CUI) values ('"+Area+"','"+Escuela+"','"+Participante+"','"+CUI+"')")
        elif (Deporte == self.lista_depor[1]):
            cursor2.execute("insert into vóley (Area,Escuela,Participante,CUI) values ('"+Area+"','"+Escuela+"','"+Participante+"','"+CUI+"')")
        elif (Deporte == self.lista_depor[2]):
            cursor2.execute("insert into basquet (Area,Escuela,Participante,CUI) values ('"+Area+"','"+Escuela+"','"+Participante+"','"+CUI+"')")
        elif (Deporte == self.lista_depor[3]):
            cursor2.execute("insert into atletismo (Area,Escuela,Participante,CUI) values ('"+Area+"','"+Escuela+"','"+Participante+"','"+CUI+"')")
        elif (Deporte == self.lista_depor[4]):
            cursor2.execute("insert into natacion (Area,Escuela,Participante,CUI) values ('"+Area+"','"+Escuela+"','"+Participante+"','"+CUI+"')")


        #cursor2.execute("insert into {} (Escuela,Puntaje,Partidos_Ganados,Partidos_Empatados, Partidos_Perdidos) values ('"+Escuela+"','0','0','0','0')".format(continente))

        conexion1.commit()
        conexion2.commit()

        conexion1.close()
        conexion2.close()
        print("Se registro con exito!")

