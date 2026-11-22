import numpy as np
from manim import (
    LEFT,
    RIGHT,
    AnimationGroup,
    Circle,
    FadeIn,
    LaggedStart,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Text,
    Transform,
    VGroup,
)

from estilo import BLANCO, BORDE, CIAN, FUENTE_CODIGO, NODO, PANEL, TENUE, texto
from programa import leer_codigo_dfs

PALABRAS_CLAVE = ["void", "int", "for", "if", "else", "while", "continue", "true", "vector"]
COLOR_PALABRA_CLAVE = "#d2a8ff"


def colores_de_sintaxis():
    colores = {}
    for palabra in PALABRAS_CLAVE:
        colores[palabra] = COLOR_PALABRA_CLAVE
    return colores


class PanelCodigo:

    def __init__(self, x_izquierda, x_derecha, y_arriba, alto_linea=0.2):
        self.lineas = leer_codigo_dfs()
        ancho = x_derecha - x_izquierda

        largo_maximo = 0
        for nivel, contenido in self.lineas:
            largo_maximo = max(largo_maximo, 2 * nivel + len(contenido))
        ancho_caracter = (ancho - 0.5) / largo_maximo
        referencia = Text("M" * 30, font=FUENTE_CODIGO, font_size=20)
        escala = ancho_caracter / (referencia.width / 30)

        self.textos = VGroup()
        self.alturas = []
        for numero, (nivel, contenido) in enumerate(self.lineas):
            linea = Text("|" + contenido, font=FUENTE_CODIGO, font_size=20, color=BLANCO, t2c=colores_de_sintaxis())
            linea.scale(escala)
            linea[0].set_opacity(0)

            y = y_arriba - 0.62 - numero * alto_linea
            x = x_izquierda + 0.25 + (2 * nivel - 1) * ancho_caracter
            linea.move_to([x, y, 0], aligned_edge=LEFT)

            self.alturas.append(y)
            self.textos.add(linea)

        alto = 0.62 + len(self.lineas) * alto_linea + 0.1
        self.centro_x = (x_izquierda + x_derecha) / 2

        self.fondo = RoundedRectangle(width=ancho, height=alto, corner_radius=0.14)
        self.fondo.set_fill(PANEL, 1)
        self.fondo.set_stroke(BORDE, 1.5)
        self.fondo.move_to([self.centro_x, y_arriba - alto / 2, 0])

        self.titulo = texto("grafo_biconexas.cpp  ·  dfsBiconexas()", 17, TENUE, fuente=FUENTE_CODIGO)
        self.titulo.move_to([x_izquierda + 0.25, y_arriba - 0.27, 0], aligned_edge=LEFT)

        franja = Rectangle(width=ancho - 0.12, height=alto_linea)
        franja.set_fill(CIAN, 0.2)
        franja.set_stroke(width=0)
        marca = Rectangle(width=0.06, height=alto_linea)
        marca.set_fill(CIAN, 1)
        marca.set_stroke(width=0)
        marca.align_to(franja, LEFT)
        self.barra = VGroup(franja, marca)
        self.barra_visible = False

        self.fondo.set_z_index(8)
        self.barra.set_z_index(9)
        self.textos.set_z_index(10)
        self.titulo.set_z_index(10)

    def aparecer(self):
        entradas = []
        for linea in self.textos:
            entradas.append(FadeIn(linea, shift=RIGHT * 0.15))
        return AnimationGroup(FadeIn(self.fondo), FadeIn(self.titulo), LaggedStart(*entradas, lag_ratio=0.04))

    def ir_a(self, fragmento):
        numero = 0
        while fragmento not in self.lineas[numero][1]:
            numero += 1
        destino = [self.centro_x, self.alturas[numero], 0]

        if not self.barra_visible:
            self.barra_visible = True
            self.barra.move_to(destino)
            return FadeIn(self.barra)
        return self.barra.animate.move_to(destino)


class PanelPila:

    def __init__(self, x_izquierda, x_derecha, y, ancho_ficha=0.95, separacion=0.1):
        self.y = y
        self.ancho_ficha = ancho_ficha
        self.separacion = separacion
        self.fichas = []

        self.rotulo = texto("pilaAristas", 20, TENUE, fuente=FUENTE_CODIGO)
        self.rotulo.move_to([x_izquierda, y, 0], aligned_edge=LEFT)
        self.x_inicio = x_izquierda + self.rotulo.width + 0.3

        self.fondo = RoundedRectangle(width=x_derecha - self.x_inicio + 0.2, height=0.72, corner_radius=0.14)
        self.fondo.set_fill(PANEL, 1)
        self.fondo.set_stroke(BORDE, 1.5)
        self.fondo.move_to([(self.x_inicio + x_derecha) / 2, y, 0])

        self.fondo.set_z_index(8)
        self.rotulo.set_z_index(8)

    def crear_ficha(self, u, v, color):
        marco = RoundedRectangle(width=self.ancho_ficha, height=0.5, corner_radius=0.12)
        marco.set_fill(NODO, 1)
        marco.set_stroke(color, 2.5)
        nombre = texto(str(u) + "-" + str(v), 20, BLANCO, fuente=FUENTE_CODIGO)

        ficha = VGroup(marco, nombre)
        posicion = len(self.fichas)
        x = self.x_inicio + 0.12 + posicion * (self.ancho_ficha + self.separacion) + self.ancho_ficha / 2
        ficha.move_to([x, self.y, 0])
        ficha.set_z_index(11)
        return ficha

    def apilar(self, u, v, color, origen):
        final = self.crear_ficha(u, v, color)
        ficha = final.copy()
        ficha.scale(0.3)
        ficha.move_to(origen)
        ficha.set_opacity(0)
        self.fichas.append(ficha)
        return Transform(ficha, final)

    def desapilar(self, cantidad):
        salen = self.fichas[-cantidad:]
        salen.reverse()
        del self.fichas[-cantidad:]
        return salen


def producto_cruz(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def envolvente_convexa(puntos):
    ordenados = sorted(puntos, key=lambda p: (p[0], p[1]))

    inferior = []
    for p in ordenados:
        while len(inferior) >= 2 and producto_cruz(inferior[-2], inferior[-1], p) <= 1e-9:
            inferior.pop()
        inferior.append(p)

    superior = []
    for p in reversed(ordenados):
        while len(superior) >= 2 and producto_cruz(superior[-2], superior[-1], p) <= 1e-9:
            superior.pop()
        superior.append(p)

    return inferior[:-1] + superior[:-1]


def capsula(a, b, margen):
    direccion = b - a
    figura = RoundedRectangle(
        width=np.linalg.norm(direccion) + 2 * margen,
        height=2 * margen,
        corner_radius=margen * 0.98,
    )
    figura.rotate(np.arctan2(direccion[1], direccion[0]))
    figura.move_to((a + b) / 2)
    return figura


def contorno(puntos, margen, color):
    puntos = [np.array(p) for p in puntos]

    if len(puntos) == 1:
        figura = Circle(radius=margen).move_to(puntos[0])
    elif len(puntos) == 2:
        figura = capsula(puntos[0], puntos[1], margen)
    else:
        esquinas = envolvente_convexa(puntos)
        if len(esquinas) < 3:
            ordenados = sorted(puntos, key=lambda p: (p[0], p[1]))
            figura = capsula(ordenados[0], ordenados[-1], margen)
        else:
            centro = sum(esquinas) / len(esquinas)
            alejadas = []
            for esquina in esquinas:
                hacia_afuera = (esquina - centro) / np.linalg.norm(esquina - centro)
                alejadas.append(esquina + 1.25 * margen * hacia_afuera)
            figura = Polygon(*alejadas)
            figura.round_corners(margen * 0.75)

    figura.set_fill(color, 0.14)
    figura.set_stroke(color, 2, 0.65)
    figura.set_z_index(-1)
    return figura
