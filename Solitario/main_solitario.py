import random
import tkinter as tk
from PIL import Image, ImageTk # Pillow permite cargar imágenes
import os

# Ruta relativa de la imagen reverso
ruta_imagen = "Solitario/Imagenes/Reverso.jpg"

# Asegurarse de la ruta
print(os.path.abspath(ruta_imagen))

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Solitario")
ventana.geometry("1024x768")

# Definimos los valores y palos de las cartas
valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
palos = ['♥', '♦', '♣', '♠']

# Fundaciones: 4 pilas vacías, una para cada palo
fundaciones = {'♥': [], '♦': [], '♣': [], '♠': []}

# Creamos la baraja como una lista de tuplas (valor, palo)
baraja = [(valor, palo) for valor in valores for palo in palos]


# Barajamos la baraja
random.shuffle(baraja)

# Columnas del solitario

columnas = []
for i in range(7):

    # Cada columna tendrá su índice + 1 cartas
    columna = [baraja.pop() for _ in range(i+1)]

    # Se ocultan las cartas menos la última
    for j in range(len(columna)-1):
        columna[j] = ('X','X') # Carta oculta
    columnas.append(columna)

# Mazo: Las cartas restantes después del reparto
mazo = baraja
descarte = [] # Pila de cartas robadas

# Cargar imagen del reverso de las cartas
imagen_reverso=Image.open(ruta_imagen).resize((80,120))
imagen_reverso=ImageTk.PhotoImage(imagen_reverso)

# Actualizar las columnas en la interfaz

def actualizar_tablero():
    for i, columna in enumerate(columnas):
        for j, carta in enumerate(columna):
            if carta == ('X','X'):
                label=tk.Label(frame_columnas[i], image=imagen_reverso)
            else:
                label=tk.Label(frame_columnas[i], text=f"{carta[0]}{carta[1]}")
            label.grid(row=j, column=0, pady=5)

# Crear frame para las columnas

frame_columnas=[tk.Frame(ventana) for _ in range(7)]
for i, frame in enumerate(frame_columnas):
    frame_columnas[i].grid(row=0, column=i, padx=10)

# Botón para robar una carta del mazo

def robar_carta():
    if mazo:
        carta = mazo.pop()
        descarte.append(carta)
        actualizar_descarte()
    else:
        print("El mazo está vacío.")

# Crear frame para el mazo y el descarte

frame_mazo =tk.Frame(ventana, bg='green')
frame_mazo.grid(row=0, column=0, columnspan=2, pady=10,padx=10)

boton_mazo = tk.Button(frame_mazo, image=imagen_reverso, command=robar_carta)
boton_mazo.grid(row=0, column=0)

# Mostrar la última carta robada en el descarte
label_descarte = tk.Label(frame_mazo, text="Descarte: ", bg='green')
label_descarte.grid(row=0,column=1, padx=10)

# Descartar cartas

def actualizar_descarte():
    if descarte:
        carta = descarte[-1]
        label_descarte.config(text=f"{carta[0]}{carta[1]}")
    else:
        label_descarte.config(text="Descarte: ")

# Verificar 2 cartas sean colores opuestos

def colores_opuestos(carta1,carta2): 
    rojas = ['♥', '♦']
    negras = ['♣', '♠']

    return (
        (carta1[1] in rojas and carta2[1] in negras) or 
        (carta1[1] in negras and carta2[1] in rojas)
    )

# Verificar si es una secuencia de cartas válida (orden descendente y colores alternados)
def secuencia_valida(secuencia):
    for i in range(len(secuencia)-1):
        carta_actual = secuencia[i]
        carta_siguiente = secuencia[i+1]
        if not (
            valores.index(carta_actual[0] == valores.index(carta_siguiente[0]) +1 and colores_opuestos(carta_actual,carta_siguiente))
        ):
            return False
    return True

# Mueve una secuencia de cartas desde una columna a otra si es válida
def mover_secuencia(origen, indice_inicial, destino):
    secuencia = columnas[origen][indice_inicial:]

    if secuencia_valida(secuencia):
        print("\nMovimiento inválido: La secuencia no es válida.")
        return
    if not columnas[destino]: # Si la columna de destino está vacía
        if secuencia[0][0] != 'K': # Solo se puede mover un Rey a una columna vacía
            print("\nMovimiento inválido: Solo un Rey puede moverse a una columna vacía.")
            return
    else: # Si la columna de destino no está vacía
        carta_destino = columnas[destino][-1]
        if not permitido_mover(secuencia[0],carta_destino):
            print("\nMovimiento inválido: La carta superior de la secuencia no encaja.")
            return
    # Movimiento válido: trasladamos la secuencia
    columnas[origen] = columnas[origen][:indice_inicial]
    columnas[destino].extend(secuencia)
    print(f"\nMovimiento exitoso: {secuencia} -> Columna {destino + 1}")

    # Si quedan cartas ocultas en la columna de orige, se descubre la última carta
    if columnas[origen] and columnas[origen][-1] == ('X', 'X'):
        columnas[origen][-1] = baraja.pop()

# Verificar que se pueda colocar la carta en la columna destino

def permitido_mover(carta,destino):
    valor_origen = valores.index(carta[0])
    valor_destino = valores.index(destino[0])

    # Se realiza el movimiento si la carta es de menor valor y color opuesto
    return valor_origen == valor_destino-1 and colores_opuestos(carta,destino)

# Mover la última carta de una columna a otra si es un movimiento válido

def mover_carta(origen,destino):
    carta_a_mover = columnas[origen][-1]

    if not columnas[destino]: # Si la columna destino está vacía
        if carta_a_mover[0] == 'K': # Solo se permite mover un rey
            columnas[origen].pop()
            columnas[destino].append(carta_a_mover)
            print(f"\nMovimiento exioso: {carta_a_mover} -> Columna {destino+1}")
        else:
            print("\nMovimiento inválido: Solo un Rey puede moverse a una columna vacía.")
    else: # Si la columna de destino no está vacía
        carta_destino = columnas[destino][-1]

        if permitido_mover(carta_a_mover,carta_destino):
            columnas[origen].pop() # Se quita la carta de la columna origen
            columnas[destino].append(carta_a_mover) # Se agrega la carta a la columna destino
            print(f"\nMovimiento exioso: {carta_a_mover} -> Columna {destino+1}")
        else:
            print("\nMovimiento inválido")
    # Si se quedan cartas ocultas en la columna de origen, se descubre la última
    if columnas[origen] and columnas[origen][-1] == ('X','X'):
        columnas[origen][-1] = baraja.pop()

# Mueve la carta del descarte a una columna si es válido

def mover_carta_desde_descarte(destino):
    if not descarte:
        print("\nNo hay cartas en el descarte.")
        return
    carta_a_mover = descarte[-1] # Carta del descarte

    # Si la columna de destino está vacía, solo se permite mover un Rey
    if not columnas[destino]: 
        if carta_a_mover[0] != 'K': 
            print("\nMovimiento inválido: Solo un Rey puede moverse a una columna vacía.")
            return
    # Si la columna de destino no está vacía, verificamos el movimiento
    elif not permitido_mover(carta_a_mover, columnas[destino][-1]):
        print("\nMovimiento inválido: La carta no encaja en la columna destino.")
        return
    
    # Movimiento válido: Quitamos la carta del descarte y la agregamos a la columna destino
    descarte.pop()
    columnas[destino].append(carta_a_mover)
    print(f"\nMovimiento exitoso: {carta_a_mover} -> Columna {destino + 1}")

# Mueve una carta desde donde sea a la fundación correspondiente

def mover_a_fundacion(origen='descarte',columna=None):
    if origen == 'descarte':
        if not descarte:
            print("\nNo hay cartas en el descarte.")
            return
        carta = descarte[-1]
    elif columna is not None:
        if not columnas[columna]:
            print(f"\nLa columna {columna + 1} está vacía.")
            return
        carta = columnas[columna][-1]
    else:
        print("\nMovimiento inválido.")
        return
    
    # Verifica si la carta se puede mover a la fundación correspondiente
    palo = carta[1]
    fundacion= fundaciones[palo]

    if not fundacion and carta[0] == 'A': # Solo un As puede iniciar una fundación
        (descarte if origen == 'descarte' else columnas[columna]).pop()
        fundacion.append(carta)
        print(f"\nMovimiento exitoso: {carta} -> Fundación {palo}")
    elif fundacion and valores.index(carta[0]) == valores.index(fundacion[-1][0])+1:
        (descarte if origen == 'descarte' else columnas[columna]).pop()
        fundacion.append(carta)
        print(f"\nMovimiento exitoso: {carta} -> Fundación {palo}")
    else:
        print("\nMovimiento inválido: No se puede mover esa carta a la fundación.")
    
# Condición de victoria

def verificar_victoria():
    if all(len(fundacion)==13 for fundacion in fundaciones.values()):
        print("\n¡Felicidades! Has ganado el juego.")
        return True
    return False

# Mostrar el tablero inicial

actualizar_tablero()

# Ejecutar la ventana

ventana.mainloop()
