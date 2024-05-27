import pygame
import requests
from io import BytesIO
import random
import heapq
import math
import time

# Función para descargar la imagen de internet
def descargar_imagen(url):
    respuesta = requests.get(url)
    return BytesIO(respuesta.content)

# Clase interna que representa un nodo en el grafo de posiciones de piezas del rompecabezas
class Nodo:
    def __init__(self, posicion):
        self.posicion = posicion
        self.nodos_adyacentes = []

# Clase interna que representa un grafo de posiciones de piezas del rompecabezas
class GrafoPuzzle:
    def __init__(self, posiciones_piezas):
        self.nodos = []
        self.lista_adyacencia = []
        self.posiciones_piezas = posiciones_piezas
        self.construir_grafo()

    # Método para calcular la distancia entre dos posiciones de piezas
    def distancia(self, pos1, pos2):
        # Utiliza la distancia Euclidiana
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    # Método para construir el grafo a partir de las posiciones de las piezas
    def construir_grafo(self):
        for posicion in self.posiciones_piezas:
            self.nodos.append(Nodo(posicion))
        
        for i, nodo in enumerate(self.nodos):
            nodos_adyacentes = []
            for j, otro_nodo in enumerate(self.nodos):
                if i != j:
                    peso = self.distancia(nodo.posicion, otro_nodo.posicion)
                    nodos_adyacentes.append((j, peso))
            self.lista_adyacencia.append(nodos_adyacentes)

    # Método que implementa el algoritmo de Prim para encontrar el Árbol de Expansión Mínima (MST)
    def prim_mst(self):
        mst = set()  # Conjunto para almacenar las aristas del MST
        visitados = [False] * len(self.nodos)
        vertice_inicial = 0  # Empieza desde el primer vértice
        visitados[vertice_inicial] = True
        aristas = [(peso, vertice_inicial, vertice) for vertice, peso in self.lista_adyacencia[vertice_inicial]]
        heapq.heapify(aristas)

        while aristas:
            peso, origen, destino = heapq.heappop(aristas)
            if not visitados[destino]:
                visitados[destino] = True
                mst.add((origen, destino))
                for vecino, peso_vecino in self.lista_adyacencia[destino]:
                    if not visitados[vecino]:
                        heapq.heappush(aristas, (peso_vecino, destino, vecino))

        return mst

# Inicializa pygame
pygame.init()

# Configuración de la pantalla
ancho_pantalla = 1000  # Aumenta el ancho de la pantalla
alto_pantalla = 600
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption('Juego de Rompecabezas')

# Configuración del reloj
reloj = pygame.time.Clock()

# URL de la imagen a usar
url_imagen = 'https://imagenes-tiernas.net/wp-content/uploads/2011/10/perro-lindo-labrador-marron.jpg'  # Cambia esto por la URL de la imagen que quieras usar

# Descargar y cargar la imagen
archivo_imagen = descargar_imagen(url_imagen)
imagen = pygame.image.load(archivo_imagen)

# Redimensionar la imagen para que se ajuste a la pantalla
imagen = pygame.transform.scale(imagen, (ancho_pantalla // 2, alto_pantalla))

# Configurar el tamaño del rompecabezas
filas, columnas = 4, 4
ancho_pieza = ancho_pantalla // (2 * columnas)
alto_pieza = alto_pantalla // filas
piezas = []

# Dividir la imagen en piezas
for i in range(filas):
    for j in range(columnas):
        rect = pygame.Rect(j * ancho_pieza, i * alto_pieza, ancho_pieza, alto_pieza)
        pieza = imagen.subsurface(rect)
        piezas.append(pieza)

# Posiciones iniciales de las piezas (ordenadas)
posiciones = [(j * ancho_pieza, i * alto_pieza) for i in range(filas) for j in range(columnas)]
posiciones_piezas = posiciones[:]

# Lista para almacenar las posiciones correctas
posiciones_correctas = posiciones[:]

# Función para dibujar piezas
def dibujar_piezas():
    for i, pieza in enumerate(piezas):
        pantalla.blit(pieza, posiciones_piezas[i])

# Función para verificar si el puzzle está resuelto
def esta_resuelto():
    for i, pos in enumerate(posiciones_piezas):
        if pos != posiciones_correctas[i]:
            return False
    return True

# Función para reordenar el rompecabezas
def desordenar_piezas():
    random.shuffle(posiciones_piezas)
    tiempo_inicio = time.time()  # Iniciar el temporizador
    contador_movimientos = 0  # Reiniciar el contador de movimientos
    puzzle_resuelto = False  # Restablecer la variable puzzle_resuelto

# Función para resolver el rompecabezas
def resolver_puzzle():
    posiciones_piezas[:] = posiciones_correctas[:]
    tiempo_inicio = time.time()  # Iniciar el temporizador
    contador_movimientos = 0  # Reiniciar el contador de movimientos
    puzzle_resuelto = False  # Restablecer la variable puzzle_resuelto

# Algoritmo de A* para encontrar el camino más corto
def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(inicio, objetivo):
    conjunto_abierto = []
    heapq.heappush(conjunto_abierto, (0, inicio))
    de_donde_vino = {}
    puntaje_g = {inicio: 0}
    puntaje_f = {inicio: heuristica(inicio, objetivo)}

    while conjunto_abierto:
        _, actual = heapq.heappop(conjunto_abierto)
        
        if actual == objetivo:
            camino = []
            while actual in de_donde_vino:
                camino.append(actual)
                actual = de_donde_vino[actual]
            camino.reverse()
            return camino
        
        vecinos = [(actual[0] + ancho_pieza, actual[1]), (actual[0] - ancho_pieza, actual[1]),
                   (actual[0], actual[1] + alto_pieza), (actual[0], actual[1] - alto_pieza)]
        
        for vecino in vecinos:
            if 0 <= vecino[0] < ancho_pantalla // 2 and 0 <= vecino[1] < alto_pantalla:  # Validación de límites
                puntaje_g_tentativo = puntaje_g[actual] + 1
                if vecino not in puntaje_g or puntaje_g_tentativo < puntaje_g[vecino]:
                    de_donde_vino[vecino] = actual
                    puntaje_g[vecino] = puntaje_g_tentativo                    
                    puntaje_f[vecino] = puntaje_g_tentativo + heuristica(vecino, objetivo)
                    if vecino not in [i[1] for i in conjunto_abierto]:
                        heapq.heappush(conjunto_abierto, (puntaje_f[vecino], vecino))

    return []

# Botones
rect_boton_desordenar = pygame.Rect(ancho_pantalla // 2 + 50, 50, 200, 50)
rect_boton_resolver = pygame.Rect(ancho_pantalla // 2 + 50, 150, 200, 50)
rect_boton_mst = pygame.Rect(ancho_pantalla // 2 + 50, 250, 200, 50)  # Agregar botón para mostrar MST

# Variables para el movimiento de las piezas
pieza_seleccionada = None
camino_sugerido = []

# Variables para el MST
aristas_mst = set()
superficie_mst = pygame.Surface((ancho_pantalla // 2 - 50, alto_pantalla - 50))  # Cambiar el tamaño de la superficie del MST
superficie_mst.fill((255, 255, 255))

# Variables para el tiempo y el contador de movimientos
tiempo_inicio = None  # Inicializado como None
contador_movimientos = 0
temporizador_corriendo = False  # Variable para controlar si el temporizador está en ejecución

# Variable para indicar si el rompecabezas está resuelto
puzzle_resuelto = False

# Bucle principal del juego
ejecutando = True
primera_vez = True
mostrar_mst = False  # Variable para mostrar el MST
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            # Verificar si se hizo clic en el botón "Desordenar"
            if evento.button == 1 and rect_boton_desordenar.collidepoint(evento.pos):
                desordenar_piezas()
                superficie_mst.fill((255, 255, 255))  # Limpiar la superficie del MST
                grafo_puzzle = GrafoPuzzle(posiciones_piezas)  # Crear el grafo de posiciones del rompecabezas
                aristas_mst = grafo_puzzle.prim_mst()  # Calcular el MST del grafo de posiciones
                tiempo_inicio = time.time()  # Iniciar el temporizador
                contador_movimientos = 0  # Reiniciar el contador de movimientos
                puzzle_resuelto = False  # Restablecer la variable puzzle_resuelto
                temporizador_corriendo = True  # Iniciar el temporizador
            # Verificar si se hizo clic en el botón "Resolver"
            elif evento.button == 1 and rect_boton_resolver.collidepoint(evento.pos):
                resolver_puzzle()
                tiempo_inicio = time.time()  # Iniciar el temporizador
                contador_movimientos = 0  # Reiniciar el contador de movimientos
                puzzle_resuelto = False  # Restablecer la variable puzzle_resuelto
                temporizador_corriendo = True  # Iniciar el temporizador
            # Verificar si se hizo clic en el botón "Mostrar MST"
            elif evento.button == 1 and rect_boton_mst.collidepoint(evento.pos):
                mostrar_mst = not mostrar_mst
            # Verificar si se hizo clic en una pieza
            else:
                for i, pos in enumerate(posiciones_piezas):
                    rect = pygame.Rect(pos[0], pos[1], ancho_pieza, alto_pieza)
                    if rect.collidepoint(evento.pos):
                        pieza_seleccionada = i
                        camino_sugerido = astar(posiciones_piezas[pieza_seleccionada], posiciones_correctas[pieza_seleccionada])
                        break
        elif evento.type == pygame.MOUSEBUTTONUP and pieza_seleccionada is not None:
            # Obtener la posición del mouse cuando se suelta el botón
            mouse_x, mouse_y = evento.pos
            pos_original = posiciones_piezas[pieza_seleccionada]

            # Determinar la nueva posición basada en la cuadrícula
            nueva_pos = (
                (mouse_x // ancho_pieza) * ancho_pieza,
                (mouse_y // alto_pieza) * alto_pieza
            )

            # Verificar si la nueva posición es adyacente a la original
            if (abs(nueva_pos[0] - pos_original[0]) == ancho_pieza and nueva_pos[1] == pos_original[1]) or \
                    (abs(nueva_pos[1] - pos_original[1]) == alto_pieza and nueva_pos[0] == pos_original[0]):
                if nueva_pos in posiciones_piezas:
                    indice_intercambio = posiciones_piezas.index(nueva_pos)
                    posiciones_piezas[pieza_seleccionada], posiciones_piezas[indice_intercambio] = posiciones_piezas[indice_intercambio], posiciones_piezas[pieza_seleccionada]
                    contador_movimientos += 1  # Incrementar el contador de movimientos
                else:
                    posiciones_piezas[pieza_seleccionada] = nueva_pos
                    contador_movimientos += 1  # Incrementar el contador de movimientos


                    # Verificar si el rompecabezas se ha resuelto
                if esta_resuelto():
                        puzzle_resuelto = True
                        # Mostrar mensaje de "¡LO LOGRASTE!"
                        fuente = pygame.font.Font(None, 72)
                        texto = fuente.render('¡LO LOGRASTE!', True, (0, 0, 0))
                        rect_texto = texto.get_rect(center=(ancho_pantalla // 2, alto_pantalla // 2))
                        pantalla.blit(texto, rect_texto)
                        pygame.display.flip()
                        # Esperar un momento antes de salir del bucle
                        pygame.time.wait(6000)
                        break  # Salir del bucle principal del juego

            pieza_seleccionada = None
            camino_sugerido = []

    pantalla.fill((255, 255, 255))

    # División para el rompecabezas
    superficie_puzzle = pygame.Surface((ancho_pantalla // 2, alto_pantalla))
    superficie_puzzle.fill((255, 255, 255))
    superficie_puzzle.blit(imagen, (0, 0))
    for i, pieza in enumerate(piezas):
        superficie_puzzle.blit(pieza, posiciones_piezas[i])
    pantalla.blit(superficie_puzzle, (0, 0))

    # Dibujar botones
    pygame.draw.rect(pantalla, (0, 255, 0), rect_boton_desordenar)
    pygame.draw.rect(pantalla, (255, 0, 0), rect_boton_resolver)
    pygame.draw.rect(pantalla, (0, 0, 255), rect_boton_mst)  # Dibujar botón para mostrar MST
    fuente = pygame.font.Font(None, 36)
    texto = fuente.render('Desordenar', True, (0, 0, 0))
    pantalla.blit(texto, (rect_boton_desordenar.x + 10, rect_boton_desordenar.y + 10))
    texto = fuente.render('Resolver', True, (0, 0, 0))
    pantalla.blit(texto, (rect_boton_resolver.x + 30, rect_boton_resolver.y + 10))
    texto = fuente.render('Mostrar MST', True, (255, 255, 255))  # Texto para el botón MST
    pantalla.blit(texto, (rect_boton_mst.x + 10, rect_boton_mst.y + 10))

    # Mostrar el MST si se ha presionado el botón correspondiente
    if mostrar_mst:
        # Dibujar el título del MST en la parte izquierda
        fuente_titulo = pygame.font.Font(None, 48)
        texto_titulo = fuente_titulo.render("¡Árbol de Expansión Mínima!", True, (0, 0, 0))
        pantalla.blit(texto_titulo, (10, 10))  # Ajusta las coordenadas x según lo necesites

    # Mostrar el tiempo transcurrido
    if temporizador_corriendo or (puzzle_resuelto and not temporizador_corriendo):
        tiempo_transcurrido = time.time() - tiempo_inicio if temporizador_corriendo else 0
        texto = fuente.render(f"Tiempo: {int(tiempo_transcurrido)}s", True, (0, 0, 0))
        pantalla.blit(texto, (ancho_pantalla // 2 + 50, alto_pantalla - 100))

    # Mostrar el contador de movimientos
    texto = fuente.render(f"Movimientos: {contador_movimientos}", True, (0, 0, 0))
    pantalla.blit(texto, (ancho_pantalla // 2 + 50, alto_pantalla - 70))

    # Mostrar el MST si se ha presionado el botón correspondiente
    if mostrar_mst:
        # Dibujar las aristas del MST en la superficie del MST
        for arista in aristas_mst:
            pygame.draw.line(superficie_mst, (0, 0, 255), posiciones_piezas[arista[0]], posiciones_piezas[arista[1]], 3)
        
        # Dibujar los nodos (piezas) en la superficie del MST
        for pos in posiciones_piezas:
            rect_nodo = pygame.Rect(pos[0] - ancho_pieza // 4, pos[1] - alto_pieza // 4, ancho_pieza // 2, alto_pieza // 2)
            pygame.draw.rect(superficie_mst, (0, 0, 0), rect_nodo)
        
        # Mostrar la superficie del MST en la pantalla
        pantalla.blit(superficie_mst, (50, 50))

    # Dibujar una bandera en la posición final del camino sugerido
    if camino_sugerido:
        pos_bandera = (camino_sugerido[-1][0] + ancho_pieza // 2, camino_sugerido[-1][1] + alto_pieza // 2)
        pygame.draw.line(pantalla, (255, 0, 0), pos_bandera, (pos_bandera[0], pos_bandera[1] - 20), 5)  # Asta de la bandera
        pygame.draw.polygon(pantalla, (255, 0, 0), [(pos_bandera[0], pos_bandera[1] - 20),
                                                    (pos_bandera[0] + 15, pos_bandera[1] - 15),
                                                    (pos_bandera[0], pos_bandera[1] - 10)])  # Bandera

    pygame.display.flip()
    reloj.tick(30)

    if primera_vez:
        primera_vez = False

    # Verificar si el puzzle está resuelto
    if esta_resuelto():
        puzzle_resuelto = True
        temporizador_corriendo = False  # Pausar el temporizador
    else:
        temporizador_corriendo = True  # Asegurarse de que el temporizador esté en ejecución si el puzzle no está resuelto

pygame.quit()