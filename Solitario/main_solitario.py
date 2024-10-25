import random
import tkinter as tk
from PIL import Image, ImageTk # Pillow permite cargar imágenes
import os

# Ruta relativa de la imagen reverso
ruta_imagen = "Solitario/Imagenes/Reverso.jpg"

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Solitario")
ventana.geometry("960x768")

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
columnas = [[baraja.pop() for _ in range(i+1)] for i in range(7)]
for i in range(7):
    # Se ocultan las cartas menos la última
    for j in range(len(columnas[i])-1):
        columnas[i][j] = ('X','X') # Carta oculta


# Mazo: Las cartas restantes después del reparto
mazo = baraja
descarte = [] # Pila de cartas robadas

# Cargar imagen del reverso de las cartas
imagen_reverso=Image.open(ruta_imagen).resize((80,120))
imagen_reverso=ImageTk.PhotoImage(imagen_reverso)

# Variables globales para control de selección

carta_seleccionada = None # (columna, indice) de la carta seleccionada

# Selecciona una carta al hacer clic en ella

def seleccionar_carta(columna, indice):
    global carta_seleccionada
    if columnas[columna][indice] != ('X', 'X'):
        carta_seleccionada = (columna, indice)
        print(f"Carta seleccionada: {columnas[columna][indice]}")

# Botón para robar una carta del mazo

def robar_carta():
    if mazo:
        carta = mazo.pop()
        descarte.append(carta)
        actualizar_descarte()
    else:
        print("El mazo está vacío.")

# Actualizar las columnas en la interfaz

def actualizar_tablero():
    for i, columna in enumerate(columnas):
        # Primero se limpia el frame de la columna antes de dibujar
        for widget in frame_columnas[i].winfo_children():
            widget.destroy()
        
        # Dibujar las cartas con desplazamiento vertical
        for j, carta in enumerate(columna):
            if carta == ('X','X'):
                # Carta oculta
                label=tk.Label(frame_columnas[i], image=imagen_reverso)
            else: 
                # Carta visible
                label=tk.Label(frame_columnas[i], text=f"{carta[0]}{carta[1]}")
                #Hacer la carta clickeable
                label.bind("<Button-1>", lambda e, col=i, idx=j: seleccionar_carta(col, idx))
            # Superposición cartas
            label.place(x=0, y=j*30)

# Crear frame para las columnas

frame_columnas=[tk.Frame(ventana, width=80, height=600) for _ in range(7)]
for i, frame in enumerate(frame_columnas):
    frame.grid(row=1, column=i, padx=10, pady=10)
    # Hacer clic izquierdo en la columna para mover la carta seleccionada
    frame.bind("<Button-1>", lambda e, destino=i: gestionar_movimiento(destino, tipo='columna'))




# Crear frame para el mazo y el descarte

frame_mazo =tk.Frame(ventana, bg='green', bd=2, relief='solid')
frame_mazo.grid(row=0, column=0, pady=10,padx=10, sticky='nw')

boton_mazo = tk.Button(frame_mazo, image=imagen_reverso, command=robar_carta)
boton_mazo.grid(row=0, column=0)

# Mostrar la última carta robada en el descarte
label_descarte = tk.Label(frame_mazo, text="Descarte: ", bg='green')
label_descarte.grid(row=0,column=1, padx=10)

# Crear frames para las fundaciones (una por palo)
frame_fundaciones = [tk.Frame(ventana, width=80, height=120, bg='white', bd=2, relief='solid') for _ in range(4)]

#Posicionarlas en la parte superior al lado del mazo
for i, frame in enumerate(frame_fundaciones):
    frame.grid(row=0, column=i+3, padx=10, pady=10)

    # Asociar cada frame a su palo correspondiente
    palo = palos[i]

    # Hacer clic izquierdo para mover del descarte o columna a fundaciones
    frame.bind("<Button-1>", lambda e, p=palo: gestionar_movimiento(p, tipo='fundacion'))

# Descartar cartas

def actualizar_descarte():
    if descarte:
        carta = descarte[-1]
        label_descarte.config(text=f"{carta[0]}{carta[1]}")
    else:
        label_descarte.config(text="Descarte: ")

# Actualizar fundaciones

def actualizar_fundaciones():
    # Recorrer cada palo y su correspondiente frame
    for i, (palo, cartas) in enumerate(fundaciones.items()):
        # Limpiar antes de actualizar
        for widget in frame_fundaciones[i].winfo_children():
            widget.destroy()
        
        if cartas: # Si ya hay cartas se muestra la última
            carta= cartas[-1]
            label = tk.Label(frame_fundaciones[i], text=f"{carta[0]}{carta[1]}")
            label.pack()
        else: # Si no hay cartas
            label = tk.Label(frame_fundaciones[i], text=f"{palo}", fg='black')
            label.pack()


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
    
    actualizar_tablero()

# Verificar que se pueda colocar la carta en la columna destino

def permitido_mover(carta,carta_destino):
    valor_origen = valores.index(carta[0])
    valor_destino = valores.index(carta_destino[0])

    # Se realiza el movimiento si la carta es de menor valor y color opuesto
    return valor_origen == valor_destino-1 and colores_opuestos(carta,carta_destino)

# Mover la última carta de una columna a otra si es un movimiento válido

def mover_carta(destino):
    global carta_seleccionada
    if carta_seleccionada is None:
        print("No has seleccionado ninguna carta.")
        return
    
    origen, indice = carta_seleccionada
    carta_a_mover = columnas[origen][indice:]

    if not columnas[destino]: # Si la columna destino está vacía
        if carta_a_mover[0][0] != 'K': # Solo se permite mover un rey
            print("Solo un Rey puede moverse a una columna vacía.")
            return
    elif not permitido_mover(carta_a_mover[0], columnas[destino][-1]):
        print("Movimiento inválido.")
        return
    
    # Realizar el movimiento
    columnas[origen]= columnas[origen][:indice]
    columnas[destino].extend(carta_a_mover)
    carta_seleccionada = None

    # Destapar la última fila
    if columnas[origen] and columnas[origen][-1] == ('X', 'X'):
        columnas[origen][-1] = mazo.pop()
    
    actualizar_tablero()

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
    actualizar_descarte()
    actualizar_tablero()
    print(f"\nMovimiento exitoso: {carta_a_mover} -> Columna {destino + 1}")

# Mueve una carta desde donde sea a la fundación correspondiente

def mover_a_fundacion(origen='descarte',columna=None, palo=None):
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
    
    # Verifica si la carta se puede mover a la fundacion correspondiente
    if palo is None:
        print("\nMovimiento inválido: La carta no coincide con la fundación.")
        return

    # Verifica si la carta se puede mover a la fundación correspondiente
    fundacion= fundaciones[palo]

    if not fundacion and carta[0] == 'A': # Solo un As puede iniciar una fundación
        (descarte if origen == 'descarte' else columnas[columna]).pop()
        fundacion.append(carta)
        print(f"\nMovimiento exitoso: {carta} -> Fundación {palo}")
    elif fundacion and valores.index(carta[0]) == valores.index(fundacion[-1][0])+1:
        (descarte if origen == 'descarte' else columnas[columna]).pop()
        descarte.pop()
        fundacion.append(carta)
        print(f"\nMovimiento exitoso: {carta} -> Fundación {palo}")
    else:
        print("\nMovimiento inválido: No se puede mover esa carta a la fundación.")
    
    # Actualizar las fundaciones después de cada movimiento 
    actualizar_fundaciones()
    actualizar_descarte()
    actualizar_tablero()
    print(f"Movimiento exitoso: {carta} -> Fundación {palo}")

    if verificar_victoria():
        print("¡Felicidades! Has ganado el juego.")
    
# Gestionar el movimiento para tener todo en un solo clic

def gestionar_movimiento(destino,tipo):
    global carta_seleccionada

    if descarte:
        if tipo =='columna':
            mover_carta_desde_descarte(destino)
        elif tipo == 'fundacion':
            mover_a_fundacion(origen='descarte', columna=None, palo=destino)
    elif carta_seleccionada:
        if tipo == 'columna':
            mover_carta(destino)
        elif tipo == 'fundacion':
            mover_a_fundacion(origen='columna', columna=carta_seleccionada[0], palo=destino)
    
    carta_seleccionada = None

# Condición de victoria

def verificar_victoria():
    if all(len(fundacion)==13 for fundacion in fundaciones.values()):
        print("\n¡Felicidades! Has ganado el juego.")
        return True
    return False

# Mostrar el tablero inicial

actualizar_tablero()
actualizar_fundaciones()

# Ejecutar la ventana

ventana.mainloop()
