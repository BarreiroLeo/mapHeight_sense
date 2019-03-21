"""
El script debe:

Conectarse con el micro.

Una vez que está en espera el micro, preguntar:
  Margenes de escaneo: [{x_inf_izq,y_inf_izq},{x2,y2},{x3,y3},{xf,yf}]
  Cantidad de puntos de escaneo: [{x_cant},{y_cant}]

Con los datos procesar:
  Dividir la distancia máxima de cada eje entre la cantidad de puntos a sensar
  El valor obtenido es el avance que hay que darle al código G (¿Coord relat?)

Posicionarse en cero automáticamente y establecer sus coordenadas Z en cero
"""

import serial
import time
# import pdb
# pdb.set_trace()
# Listar dispositivos en terminal:
# ls /dev/ttyAC*
# Instancia de objeto serial
ard_serial = serial.Serial('/dev/ttyACM0', 115200, timeout=0.5)


def input_datos():
    print("Margenes de escaneo:")
    # x_inf_izq = float(input("X inferior izq: "))
    # y_inf_izq = float(input("Y inferior izq: "))
    # x_sup_der = float(input("X superior der: "))
    # y_sup_der = float(input("Y superior der: "))

    # Imprimir posiciones para verificar la entrada de datos
    # n_puntos_x = float(input("Cantidad de puntos en X: "))
    # n_puntos_y = float(input("Cantidad de puntos en Y: "))
    x_inf_izq = 0
    y_inf_izq = 0
    x_sup_der = 10
    y_sup_der = 10
    n_puntos_x = 2
    n_puntos_y = 2
    avance_x = (x_sup_der - x_inf_izq) / n_puntos_x
    avance_y = (y_sup_der - y_inf_izq) / n_puntos_y

    tupla_posiciones = (x_inf_izq, y_inf_izq, x_sup_der, y_sup_der)
    print("TuplaPosiciones: " + str(tupla_posiciones))
    print("Avance X: " + str(avance_x))
    print("Avance Y: " + str(avance_y))


def wake_up_grbl():
    # Wake up grbl
    bytes_to_send = b'\r\n\r\n'
    ard_serial.write(bytes_to_send)
    time.sleep(2)   # Wait for grbl to initialize
    ard_serial.flushInput()  # Flush startup text in serial input


def send_to_serial(gcode):
    """
    Recibe un array con dos elementos:
    Elemento 1: Gcode
    Elemento 2: Tipo de mensaje de retorno
    """

    print(gcode[0])
    command_to_send = gcode[0] + "\r\n"
    ard_serial.write(bytes(command_to_send, encoding="ascii"))
    while True:
        grbl_says = str(ard_serial.readline())
        # if grbl_says != '':               # Imprimir los mensajes no vacíos
        #    print("Grbl says: " + grbl_says)
        if gcode[1] == 1:
            if grbl_says.find("ok") > (-1):     # Cuando encuentre ok, salir.
                break
        if gcode[1] == 2:
            if grbl_says.find("PRB") > (-1):    # Cuando encuentre PRB, salir.
                print("Grbl says: " + grbl_says + "\n")
                break


def mapear():
    # Verificar que la linea esté desocupada
    while True:
        grbl_says = str(ard_serial.readline())
        if grbl_says != '':                 # Imprimir los mensajes no vacíos
            print("Grbl says: " + grbl_says)
        if grbl_says.find("''") > (-1):     # Si hay mensaje vacío (timeout)
            break                           # Salir del while

    gcodes = [["G91", 1],             # Tupla de tuplas:
              ["G1 Z1 F50", 1],       # 1er elemento: gcode
              ["G38.2 Z-10 F50", 2],  # 2do elemento: tipo mensaje de retorno
              ["G38.5 Z01 F50", 2],     # Tipo 1: "ok"
              ["G38.2 Z-1 F10", 2],     # Tipo 2: "PRB"
              ["G38.5 Z01 F10", 2],
              ["G38.2 Z-1 F10", 2],
              ["G38.5 Z01 F10", 2],
              ["G38.2 Z-1 F10", 2],
              ["G38.5 Z01 F10", 2],
              # ["G92 Z0", 1],      # Establece coordenadas en Z = 0
              # ["?", 1],
              # ["G04 P5", 1],     # Pausa de 1seg
              # ["?", 1],
              ["$X", 1],
              ["M2", 1]
              ]

    for i in range(len(gcodes)):
        send_to_serial(gcodes[i])

    return 1


def close_serial():
    ard_serial.close()
    return 1


def main():
    # Open grbl serial port
    input_datos()
    wake_up_grbl()
    mapear()
    close_serial()


main()
