import pygame
import random
import os

# Inicializar pygame
pygame.init()

# Crear ventana principal
ANCHO, ALTO= 960,768
pantalla = pygame.display.set_mode((ANCHO,ALTO))
pygame.display.set_caption("Solitario")

# Definir colores
VERDE = (0,128,0)

# Ruta de imagenes

RUTA_IMAGENES = "Solitario/Imagenes"

# Función cargar imágenes

def cargar_imagen(nombre, ancho=80, alto=120):
    imagen = pygame.image.load(os.path.join(RUTA_IMAGENES,nombre)).convert_alpha()
    return pygame.transform.scale(imagen,(ancho,alto))

REVERSO = cargar_imagen("Reverso.png")

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

# Control del arrastre
carta_arrastrada = None
offset_x, offset_y = 0,0

# Dibujar la pantalla inicial

def dibujar_tablero():
    pantalla.fill(VERDE)

    # Dibujar el mazo
    if mazo:
        pantalla.blit(REVERSO, (50,50))
    else:
        pygame.draw.rect(pantalla, (255, 255, 255),(50,50,80,120),2)
    
    # Dibujar el descarte

    if descarte:
        carta = descarte[-1]
        dibujar_carta(carta, 150,50)
    
    # Dibujar las columnas

    for i, columna in enumerate(columnas):
        x = 50 + i*100
        for j, carta in enumerate(columna):
            y= 200 + j*30
            if carta == ('X','X'):
                pantalla.blit(REVERSO, (x,y))
            else:
                dibujar_carta(carta,x,y)
    
    # Dibujar las fundaciones

    for i, (palo, cartas) in enumerate(fundaciones.items()):
        x = 450 + i*100
        if cartas:
            dibujar_carta(cartas[-1], x, 50)
        else:
            pygame.draw.rect(pantalla, (255, 255, 255), (x, 50, 80, 120), 2)

# Dibujar una carta específica

def dibujar_carta(carta, x, y):
    valor, palo = carta
    texto = f"{valor}{palo}"
    fuente = pygame.font.Font(None, 36)
    superficie_texto = fuente.render(texto, True, (0, 0, 0))
    pygame.draw.rect(pantalla, (255, 255, 255), (x, y, 80, 120))
    pantalla.blit(superficie_texto, (x +10, y+40))

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
    global mazo, descarte

    if not mazo:
        if not descarte:
            print("\nNo hay más cartas en el mazo ni en el descarte.")
            return
        # Rellena el mazo con el descarte (excepto la última carta)
        mazo = descarte[:-1]
        descarte = [descarte[-1]]
        print("\nEl mazo ha sido recargado.")
    else:
        # Mueve una carta del mazo al descarte
        carta = mazo.pop()
        descarte.append(carta)
        print(f"\nHas robado la carta: {carta}")

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

    if not columnas[destino] and carta_a_mover[0][0] != 'K': # Solo se permite mover un rey
            print("Solo un Rey puede moverse a una columna vacía.")
            return
    elif columnas[destino] and not permitido_mover(carta_a_mover[0], columnas[destino][-1]):
        print("Movimiento inválido.")
        return
    
    # Realizar el movimiento
    columnas[origen]= columnas[origen][:indice]
    columnas[destino].extend(carta_a_mover)
    carta_seleccionada = None

    # Destapar la última fila
    if columnas[origen] and columnas[origen][-1] == ('X', 'X'):
        columnas[origen][-1] = mazo.pop()

# Mueve la carta del descarte a una columna si es válido

def mover_carta_desde_descarte(destino):
    if not descarte:
        print("\nNo hay cartas en el descarte.")
        return
    carta_a_mover = descarte[-1] # Carta del descarte

    # Si la columna de destino está vacía, solo se permite mover un Rey
    if not columnas[destino] and carta_a_mover[0] != 'K': 
            print("\nMovimiento inválido: Solo un Rey puede moverse a una columna vacía.")
            return
    # Si la columna de destino no está vacía, verificamos el movimiento
    elif columnas[destino] and not permitido_mover(carta_a_mover, columnas[destino][-1]):
        print("\nMovimiento inválido: La carta no encaja en la columna destino.")
        return
    
    # Movimiento válido: Quitamos la carta del descarte y la agregamos a la columna destino
    descarte.pop()
    columnas[destino].append(carta_a_mover)
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


# Función principal del juego

def main():
    global carta_arrastrada, offset_x, offset_y

    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if mazo and pygame.Rect(50, 50, 80, 120).collidepoint(evento.pos):
                    if mazo:
                        carta= mazo.pop()
                        descarte.append(carta)

                # Verificar si una carta del tablero fue seleccionada

                for i, columna in enumerate(columnas):
                    x= 50+ i*100
                    for j, carta in enumerate(columna):
                        y= 200 + j*30
                        if pygame.Rect(x,y,80,120).collidepoint(evento.pos):
                            carta_arrastrada=(carta, i, j)
                            offset_x = x- evento.pos[0]
                            offset_y = y- evento.pos[1]
                            seleccionar_carta(i,j)

            elif evento.type == pygame.MOUSEBUTTONUP:
                carta_arrastrada = None

            elif evento.type == pygame.MOUSEMOTION:
                if carta_arrastrada:
                    carta, col, idx = carta_arrastrada
                    x = evento.pos[0] + offset_x
                    y = evento.pos[1] + offset_y
                    dibujar_carta(carta, x, y)
        
        dibujar_tablero()
        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()

# Ejecutar el juego

if __name__ == "__main__":
    main()