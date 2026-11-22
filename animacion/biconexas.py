from collections import deque

import numpy as np
from manim import *

from estilo import (
    AMARILLO,
    BLANCO,
    BORDE,
    CIAN,
    FONDO,
    FUENTE_CODIGO,
    NODO,
    PANEL,
    ROJO,
    TENUE,
    VERDE,
    color_componente,
    texto,
)
from paneles import PanelCodigo, PanelPila, colores_de_sintaxis
from programa import leer_codigo_dfs, leer_mediciones, leer_traza
from vista import VistaGrafo

POSICIONES = {
    "principal": {
        1: (-3.2, 1.5),
        2: (-3.2, -1.5),
        3: (-1.9, 0),
        4: (-0.4, 0),
        5: (0.8, 1.5),
        6: (2.0, 0),
        7: (0.8, -1.5),
        8: (3.4, 1.4),
        9: (3.4, -1.4),
    },
    "raiz": {
        1: (0, 0),
        2: (-1.5, 1.1),
        3: (-1.5, -1.1),
        4: (1.5, 1.1),
        5: (1.5, -1.1),
    },
    "camino": {
        1: (-1.9, 0),
        2: (-0.95, 0),
        3: (0, 0),
        4: (0.95, 0),
        5: (1.9, 0),
    },
    "ciclo": {},
    "aislado": {1: (0, 0)},
}

for i in range(1, 6):
    angulo = PI / 2 + (i - 1) * TAU / 5
    POSICIONES["ciclo"][i] = (1.15 * np.cos(angulo), 1.15 * np.sin(angulo))

NOMBRES = "Leonardo Alca   ·   Luis Nieva   ·   Enrique Zheng"
CURSO = "CS2023 Algoritmos y Estructuras de Datos   ·   UTEC   ·   2026-2"


def camino_mas_corto(vecinos, origen, destino, prohibidos):
    anterior = {origen: None}
    cola = deque([origen])
    while cola:
        actual = cola.popleft()
        if actual == destino:
            camino = []
            while actual is not None:
                camino.append(actual)
                actual = anterior[actual]
            camino.reverse()
            return camino
        for vecino in vecinos[actual]:
            if vecino not in anterior and vecino not in prohibidos:
                anterior[vecino] = actual
                cola.append(vecino)
    return None


def dos_caminos_disjuntos(aristas):
    vecinos = {}
    for a, b in aristas:
        vecinos.setdefault(a, []).append(b)
        vecinos.setdefault(b, []).append(a)

    vertices = sorted(vecinos)
    for a in vertices:
        for b in vertices:
            if a < b and b not in vecinos[a]:
                primero = camino_mas_corto(vecinos, a, b, set())
                intermedios = set(primero[1:-1])
                segundo = camino_mas_corto(vecinos, a, b, intermedios)
                if segundo is not None:
                    return primero, segundo
    return None


def distancia_al_centro(v):
    x, y = POSICIONES["principal"][v]
    return np.hypot(x, y)


def con_separador_de_miles(valor):
    return f"{valor:,}".replace(",", " ")


class EscenaBase(Scene):
    def setup(self):
        self.inicio_parte = 0.0
        self.rotulos = {}

    def esperar_hasta(self, segundo):
        falta = self.inicio_parte + segundo - self.renderer.time
        if falta > 1 / 120:
            self.wait(falta)
        elif falta < -0.05:
            print(f"[AVISO] el segundo {segundo:.1f} llego {-falta:.2f} s tarde")

    def limpiar(self, duracion=0.6):
        salidas = [FadeOut(objeto) for objeto in self.mobjects]
        self.play(*salidas, run_time=duracion)
        self.rotulos = {}

    def cambiar_rotulo(self, lugar, mensaje, tam=None, color=BLANCO, resaltar=None):
        animaciones = []

        anterior = self.rotulos.get(lugar)
        if anterior is not None:
            animaciones.append(FadeOut(anterior, shift=UP * 0.15))
            self.rotulos[lugar] = None

        if mensaje:
            if lugar == "arriba":
                nuevo = texto(mensaje, tam or 38, color, weight=BOLD, t2c=resaltar or {})
                nuevo.move_to(UP * 3.4)
            else:
                nuevo = texto(mensaje, tam or 28, color, t2c=resaltar or {})
                nuevo.move_to(DOWN * 3.4)
            nuevo.set_z_index(12)
            self.rotulos[lugar] = nuevo
            animaciones.append(FadeIn(nuevo, shift=UP * 0.15))
        return animaciones


    def parte1(self):
        self.inicio_parte = self.renderer.time
        traza = leer_traza("principal")
        resumen = traza[-1]
        componentes = [evento for evento in traza if evento["ev"] == "componente"]
        mas_grande = max(componentes, key=lambda componente: len(componente["aristas"]))

        self.mostrar_titulo()

        vista = VistaGrafo(
            self, traza, POSICIONES["principal"],
            centro=DOWN * 0.15, escala=1.45, radio=0.36, con_etiquetas=False, tam_numero=30,
        )
        self.mostrar_falla_de_un_nodo(vista, resumen)
        self.mostrar_componentes(vista, componentes, mas_grande, resumen["articulaciones"])
        self.mostrar_usos(vista)
        self.comparar_metodos(vista)
        self.explicar_tin_y_low(traza, mas_grande)

    def mostrar_titulo(self):
        titulo = texto("Componentes biconexas", 68, weight=BOLD).move_to(UP * 1.1)
        raya = Line(LEFT * 3.4, RIGHT * 3.4, color=CIAN, stroke_width=4).next_to(titulo, DOWN, buff=0.35)
        subtitulo = texto("un solo DFS, dos números por nodo y una pila de aristas", 28, CIAN)
        subtitulo.next_to(raya, DOWN, buff=0.35)
        nombres = texto(NOMBRES, 30).next_to(subtitulo, DOWN, buff=0.9)
        curso = texto(CURSO, 22, TENUE).to_edge(DOWN, buff=0.5)

        self.play(Write(titulo), run_time=1.4)
        self.play(Create(raya), FadeIn(subtitulo, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(nombres), FadeIn(curso), run_time=0.8)
        self.esperar_hasta(6.4)
        self.limpiar(0.6)

    def mostrar_falla_de_un_nodo(self, vista, resumen):
        articulaciones = resumen["articulaciones"]

        comunes = [v for v in range(1, vista.n + 1) if v not in articulaciones]
        comun = min(comunes, key=distancia_al_centro)
        critico = min(articulaciones, key=distancia_al_centro)

        self.play(vista.aparecer(), *self.cambiar_rotulo("arriba", "¿Y si falla un solo nodo?"), run_time=2.0)

        self.esperar_hasta(13.0)
        self.play(
            *vista.quitar_vertice(comun),
            *self.cambiar_rotulo("abajo", f"sin el nodo {comun} la red sigue conectada: hay otro camino", color=VERDE),
            run_time=1.0,
        )
        self.esperar_hasta(17.6)
        self.play(*vista.restaurar_vertice(), *self.cambiar_rotulo("abajo", ""), run_time=0.8)

        self.esperar_hasta(19.2)
        grupos = resumen["al_quitar"][str(critico)]
        if max(grupos) == 2:
            partes = "dos"
        else:
            partes = str(max(grupos))
        self.play(
            *vista.quitar_vertice(critico, grupos, separacion=0.5),
            *self.cambiar_rotulo("abajo", f"sin el nodo {critico} la red se parte en {partes}", color=ROJO),
            run_time=1.3,
        )
        self.esperar_hasta(23.2)
        self.play(*vista.restaurar_vertice(), run_time=0.8)

        marcas = [vista.marcar_articulacion(v) for v in articulaciones]
        self.play(*marcas, *self.cambiar_rotulo("abajo", "puntos de articulación", color=ROJO), run_time=0.9)
        self.esperar_hasta(27.0)

    def mostrar_componentes(self, vista, componentes, mas_grande, articulaciones):
        coloreados = []
        for componente in componentes:
            coloreados.append(AnimationGroup(*vista.colorear_componente(componente, incluir_u=True)))
        self.play(
            *self.cambiar_rotulo("arriba", "Componente biconexa"),
            *self.cambiar_rotulo(
                "abajo", "un pedazo máximo que sigue conectado aunque le quites cualquier vértice", tam=26
            ),
            LaggedStart(*coloreados, lag_ratio=0.4),
            run_time=3.6,
        )

        self.esperar_hasta(35.5)
        trazos = VGroup()
        caminos = dos_caminos_disjuntos(mas_grande["aristas"])
        if caminos is not None:
            for camino, color in zip(caminos, [WHITE, AMARILLO]):
                trazo = VMobject()
                trazo.set_points_as_corners([vista.posicion[v] for v in camino])
                trazo.set_stroke(color, 9)
                trazo.set_z_index(2)
                trazos.add(trazo)

            a = caminos[0][0]
            b = caminos[0][-1]
            mensaje = f"entre {a} y {b} hay dos caminos que no comparten ningún nodo intermedio"
            self.play(*self.cambiar_rotulo("abajo", mensaje, tam=26), run_time=0.6)
            self.play(Create(trazos[0]), Create(trazos[1]), run_time=2.0)
            self.play(
                Indicate(vista.circulo[a], color=WHITE, scale_factor=1.25),
                Indicate(vista.circulo[b], color=WHITE, scale_factor=1.25),
                run_time=1.0,
            )

        self.esperar_hasta(42.3)
        arcos = []
        for v in articulaciones:
            numeros = vista.componentes_de[v]
            porcion = TAU / len(numeros)
            for orden, numero in enumerate(numeros):
                arco = Arc(radius=vista.radio + 0.13, start_angle=PI / 2 + orden * porcion, angle=porcion - 0.25)
                arco.set_stroke(vista.color_de_componente[numero], 7)
                arco.move_arc_center_to(vista.posicion[v])
                arco.set_z_index(3)
                vista.todo.add(arco)
                arcos.append(Create(arco))

        anillos = [FadeOut(vista.anillo[v]) for v in articulaciones]
        mensaje = "reparten las aristas, no los vértices: una articulación pertenece a varias"
        self.play(FadeOut(trazos), *anillos, *arcos, *self.cambiar_rotulo("abajo", mensaje, tam=26), run_time=1.4)
        for v in articulaciones:
            vista.todo.remove(vista.anillo[v])
        self.esperar_hasta(50.0)

    def mostrar_usos(self, vista):
        self.play(
            vista.todo.animate.scale(0.58).move_to(LEFT * 4.05 + DOWN * 0.1),
            *self.cambiar_rotulo("arriba", "¿Para qué sirve?"),
            *self.cambiar_rotulo("abajo", ""),
            run_time=1.2,
        )

        usos = [
            ("Encontrar puntos únicos de falla", 51.6),
            ("Redes de datos, eléctricas y de transporte", 54.3),
            ("Diseñar redes tolerantes a fallos", 57.6),
            ("Es la base del block-cut tree", 60.2),
        ]
        self.lista_de_usos = VGroup()
        for orden, (frase, segundo) in enumerate(usos):
            vineta = Square(0.16)
            vineta.set_fill(color_componente(orden), 1)
            vineta.set_stroke(width=0)
            fila = VGroup(vineta, texto(frase, 25)).arrange(RIGHT, buff=0.28)
            fila.move_to([-0.45, 1.45 - orden * 0.95, 0], aligned_edge=LEFT)
            self.lista_de_usos.add(fila)

            self.esperar_hasta(segundo)
            self.play(FadeIn(fila, shift=RIGHT * 0.3), run_time=0.6)
        self.esperar_hasta(63.0)

    def comparar_metodos(self, vista):
        ingenuo = VGroup(
            texto("Método ingenuo", 32, ROJO, weight=BOLD),
            texto("quitar cada vértice y volver a recorrer el grafo", 24, TENUE),
            texto("O(V · (V + E))", 40, ROJO, fuente=FUENTE_CODIGO),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        ingenuo.move_to([-0.45, 1.25, 0], aligned_edge=LEFT)

        self.play(
            FadeOut(self.lista_de_usos),
            FadeIn(ingenuo, shift=UP * 0.2),
            *self.cambiar_rotulo("arriba", "¿Cómo las encontramos?"),
            run_time=0.8,
        )

        for v in range(1, vista.n + 1):
            self.play(*vista.quitar_vertice(v), run_time=0.24)
            self.play(*vista.restaurar_vertice(), run_time=0.24)

        self.esperar_hasta(70.2)
        un_dfs = VGroup(
            texto("Un solo DFS", 32, VERDE, weight=BOLD),
            texto("con dos números por nodo: tin y low", 24, TENUE),
            texto("O(V + E)", 40, VERDE, fuente=FUENTE_CODIGO),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        un_dfs.move_to([-0.45, -1.5, 0], aligned_edge=LEFT)
        self.play(FadeIn(un_dfs, shift=UP * 0.2), run_time=0.8)

        self.esperar_hasta(73.6)
        self.limpiar(0.6)

    def explicar_tin_y_low(self, traza, componente):
        resumen = traza[-1]

        vertices = set()
        for a, b in componente["aristas"]:
            vertices.add(a)
            vertices.add(b)
        vertices = sorted(vertices, key=lambda v: resumen["tin"][v - 1])

        retroceso = None
        for evento in traza:
            if evento["ev"] == "retroceso" and evento["u"] in vertices and evento["v"] in vertices:
                retroceso = evento
                break

        alturas = np.linspace(2.0, -1.9, len(vertices))
        posicion = {}
        nodo = {}
        rotulo_tin = {}
        rotulo_low = {}
        for v, y in zip(vertices, alturas):
            posicion[v] = np.array([-3.3, y, 0.0])

            circulo = Circle(radius=0.36)
            circulo.set_fill(NODO, 1)
            circulo.set_stroke(CIAN, 3)
            nodo[v] = VGroup(circulo, texto(str(v), 30, weight=BOLD)).move_to(posicion[v])
            nodo[v].set_z_index(3)

            rotulo_tin[v] = texto(f"tin = {resumen['tin'][v - 1]}", 26, BLANCO, fuente=FUENTE_CODIGO)
            rotulo_tin[v].move_to(posicion[v] + RIGHT * 0.75, aligned_edge=LEFT)

            rotulo_low[v] = texto(f"low = {resumen['low'][v - 1]}", 26, AMARILLO, fuente=FUENTE_CODIGO, weight=BOLD)
            rotulo_low[v].move_to(posicion[v] + RIGHT * 2.35, aligned_edge=LEFT)

        ramas = []
        for a, b in zip(vertices, vertices[1:]):
            rama = Line(posicion[a], posicion[b], color=CIAN, stroke_width=6)
            rama.set_z_index(1)
            ramas.append(rama)

        definicion_tin = VGroup(
            texto("tin[u]", 36, BLANCO, fuente=FUENTE_CODIGO, weight=BOLD),
            texto("el instante en que el DFS\ndescubre al nodo u", 25, TENUE, line_spacing=0.9),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        definicion_tin.move_to([1.4, 1.75, 0], aligned_edge=LEFT)

        definicion_low = VGroup(
            texto("low[u]", 36, AMARILLO, fuente=FUENTE_CODIGO, weight=BOLD),
            texto(
                "el tin más antiguo que alcanza\nel subárbol de u usando, a lo más,\nuna arista de retroceso",
                25, TENUE, line_spacing=0.9,
            ),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        definicion_low.move_to([1.4, -0.9, 0], aligned_edge=LEFT)

        entradas = []
        for v in vertices:
            entradas.append(AnimationGroup(FadeIn(nodo[v], scale=0.5), FadeIn(rotulo_tin[v], shift=RIGHT * 0.2)))
        self.play(
            *self.cambiar_rotulo("arriba", "Dos números por nodo"),
            FadeIn(definicion_tin, shift=UP * 0.2),
            LaggedStart(*entradas, lag_ratio=0.5),
            LaggedStart(*[Create(rama) for rama in ramas], lag_ratio=0.5),
            run_time=2.6,
        )

        self.esperar_hasta(78.2)
        arco = ArcBetweenPoints(
            posicion[retroceso["u"]] + LEFT * 0.36,
            posicion[retroceso["v"]] + LEFT * 0.36,
            angle=-PI * 0.75,
        )
        punteado = DashedVMobject(arco, num_dashes=26).set_stroke(AMARILLO, 5)
        nota = texto("arista de retroceso", 22, AMARILLO).rotate(PI / 2).next_to(arco, LEFT, buff=0.2)
        self.play(FadeIn(definicion_low, shift=UP * 0.2), Create(punteado), FadeIn(nota), run_time=1.4)

        chispa = Dot(radius=0.1, color=AMARILLO).move_to(arco.get_start())
        chispa.set_z_index(6)
        self.play(MoveAlongPath(chispa, arco), run_time=1.0)

        apariciones = [FadeIn(rotulo_low[v], shift=UP * 0.25) for v in reversed(vertices)]
        self.play(FadeOut(chispa, scale=2.5), LaggedStart(*apariciones, lag_ratio=0.55), run_time=2.6)

        self.esperar_hasta(84.4)
        self.limpiar(0.6)


    def parte2(self):
        self.inicio_parte = self.renderer.time
        traza = leer_traza("principal")

        codigo = PanelCodigo(1.25, 6.95, 3.82)
        pila = PanelPila(-6.9, 6.95, -3.4)
        vista = VistaGrafo(
            self, traza, POSICIONES["principal"],
            centro=[-2.95, 0.55, 0], escala=1.05, radio=0.3,
            codigo=codigo, pila=pila, lugar_estado=np.array([-6.85, 3.5, 0]),
        )

        nombres = VGroup(
            texto("tin", 18, BLANCO, fuente=FUENTE_CODIGO),
            texto("·", 18, TENUE, fuente=FUENTE_CODIGO),
            texto("low", 18, AMARILLO, fuente=FUENTE_CODIGO, weight=BOLD),
        ).arrange(RIGHT, buff=0.09)
        fondo = RoundedRectangle(width=nombres.width + 0.3, height=0.36, corner_radius=0.18)
        fondo.set_fill(PANEL, 1)
        fondo.set_stroke(BORDE, 1.5)
        leyenda = VGroup(fondo, nombres).move_to([-6.85, -2.35, 0], aligned_edge=LEFT)

        regla = texto(
            "low[v] ≥ tin[u]   →   el subárbol de v no escapa por encima de u",
            22, BLANCO, t2c={"low[v] ≥ tin[u]": VERDE},
        )
        if regla.width > 6.1:
            regla.scale(6.1 / regla.width)
        regla.move_to([0.95, -2.37, 0], aligned_edge=RIGHT)

        presentacion = vista.mostrar_estado("Ejecución real: cada paso lo emite nuestro programa en C++", color=TENUE)
        self.play(vista.aparecer(), *presentacion, run_time=1.6)
        self.play(codigo.aparecer(), run_time=2.2)
        self.play(FadeIn(pila.fondo), FadeIn(pila.rotulo), FadeIn(leyenda), run_time=0.8)
        self.esperar_hasta(12.0)

        tras_primer_retroceso = vista.buscar_evento(lambda e: e["ev"] == "retroceso") + 1
        primer_cierre = vista.buscar_evento(lambda e: e["ev"] == "retorno" and e["cumple"])
        tras_primera_componente = vista.buscar_evento(lambda e: e["ev"] == "componente") + 1
        final = len(vista.eventos)

        vista.reproducir(0, tras_primer_retroceso, 30.0)
        self.esperar_hasta(30.0)

        vista.reproducir(tras_primer_retroceso, primer_cierre, 46.4)
        self.esperar_hasta(46.4)

        self.play(FadeIn(regla, shift=UP * 0.2), run_time=0.6)
        vista.reproducir(primer_cierre, tras_primera_componente, 68.6)
        self.esperar_hasta(69.0)

        vista.reproducir(tras_primera_componente, final, 82.0)

        articulaciones = ", ".join(str(v) for v in vista.resumen["articulaciones"])
        cierre = vista.mostrar_estado(
            f"{vista.resumen['componentes']} componentes biconexas   ·   articulaciones: {articulaciones}",
            resaltar={"articulaciones": ROJO},
        )
        self.play(*cierre, FadeOut(codigo.barra), run_time=0.6)
        self.esperar_hasta(84.4)
        self.limpiar(0.6)


    def parte3(self):
        self.inicio_parte = self.renderer.time
        self.mostrar_caso_de_la_raiz()
        self.mostrar_casos_borde()
        self.mostrar_complejidad()
        self.mostrar_block_cut_tree()
        self.mostrar_creditos()

    def mostrar_caso_de_la_raiz(self):
        traza = leer_traza("raiz")
        vista = VistaGrafo(
            self, traza, POSICIONES["raiz"],
            centro=[-3.7, 0.1, 0], escala=1.25, radio=0.34,
            lugar_estado=np.array([-6.85, -2.75, 0]),
        )
        raiz = vista.eventos[0]["u"]

        linea_raiz = ""
        for nivel, contenido in leer_codigo_dfs():
            if "hijosRaiz > 1" in contenido:
                linea_raiz = contenido

        aviso = texto("En la raíz, low[v] ≥ tin[raíz] se cumple siempre:", 24, TENUE)
        aviso_2 = texto("esa condición no nos dice nada.", 24, TENUE)
        regla = texto("La raíz es articulación solo si tiene", 28)
        regla_2 = texto("más de un hijo en el árbol del DFS", 28, t2c={"más de un hijo": CIAN}, weight=BOLD)

        linea = Text(linea_raiz, font=FUENTE_CODIGO, font_size=20, color=BLANCO, t2c=colores_de_sintaxis())
        if linea.width > 5.6:
            linea.scale(5.6 / linea.width)
        marco = RoundedRectangle(width=linea.width + 0.5, height=0.6, corner_radius=0.14)
        marco.set_fill(PANEL, 1)
        marco.set_stroke(BORDE, 1.5)
        codigo = VGroup(marco, linea)

        rotulo_contador = texto("hijos de la raíz:", 30)

        panel = VGroup(aviso, aviso_2, regla, regla_2, codigo, rotulo_contador)
        panel.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        regla.shift(DOWN * 0.25)
        regla_2.shift(DOWN * 0.25)
        codigo.shift(DOWN * 0.45)
        rotulo_contador.shift(DOWN * 0.8)
        if panel.width > 6.2:
            panel.scale_to_fit_width(6.2)
        panel.move_to([0.6, 0.35, 0], aligned_edge=LEFT)

        contador = texto("0", 54, CIAN, fuente=FUENTE_CODIGO, weight=BOLD)
        contador.next_to(rotulo_contador, RIGHT, buff=0.35)

        self.play(
            vista.aparecer(),
            *self.cambiar_rotulo("arriba", "Un caso especial: la raíz del DFS"),
            FadeIn(VGroup(aviso, aviso_2), shift=UP * 0.2),
            run_time=1.6,
        )
        self.esperar_hasta(5.0)
        self.play(
            FadeIn(VGroup(regla, regla_2), shift=UP * 0.2),
            FadeIn(codigo, shift=UP * 0.2),
            FadeIn(rotulo_contador),
            FadeIn(contador),
            run_time=1.0,
        )

        ultimo = len(vista.eventos) - 1
        bajadas_de_la_raiz = []
        for indice, evento in enumerate(vista.eventos):
            if evento["ev"] == "arbol" and evento["u"] == raiz:
                bajadas_de_la_raiz.append(indice)

        comienzo = self.renderer.time - self.inicio_parte
        duracion = 8.2
        peso_total = vista.peso(0, ultimo)
        hijos = 0
        hecho = 0
        for corte in bajadas_de_la_raiz + [ultimo]:
            if corte > hecho:
                limite = comienzo + duracion * vista.peso(0, corte) / peso_total
                vista.reproducir(hecho, corte, limite)
            hecho = corte

            if corte in bajadas_de_la_raiz:
                hijos += 1
                nuevo = texto(str(hijos), 54, CIAN, fuente=FUENTE_CODIGO, weight=BOLD).move_to(contador)
                self.add(nuevo)
                self.remove(contador)
                contador = nuevo

        self.esperar_hasta(14.4)
        vista.reproducir(ultimo, ultimo + 1, 16.0)
        self.play(Indicate(contador, color=ROJO, scale_factor=1.4), run_time=0.8)
        self.esperar_hasta(17.4)
        self.limpiar(0.6)

    def mostrar_casos_borde(self):
        casos = [
            ("camino", "Un camino o un árbol", "cada arista, una componente", -4.5, 20.6, 5.0),
            ("ciclo", "Un ciclo", "todo el grafo, una sola componente", 0.0, 27.6, 4.6),
            ("aislado", "Un vértice aislado", "la pila nunca recibe aristas", 4.65, 33.4, 1.4),
        ]

        vistas = []
        titulos = VGroup()
        for instancia, titulo, nota, x, segundo, duracion in casos:
            vista = VistaGrafo(
                self, leer_traza(instancia), POSICIONES[instancia],
                centro=[x, 0.45, 0], radio=0.28, con_etiquetas=False, tam_numero=24,
            )
            vistas.append(vista)
            titulos.add(texto(titulo, 26, weight=BOLD).move_to([x, 2.35, 0]))

        self.play(
            *self.cambiar_rotulo("arriba", "Casos borde, con el mismo código"),
            FadeIn(titulos, shift=UP * 0.2),
            *[vista.aparecer() for vista in vistas],
            run_time=1.6,
        )

        for (instancia, titulo, nota, x, segundo, duracion), vista in zip(casos, vistas):
            self.esperar_hasta(segundo)
            vista.reproducir(0, len(vista.eventos), segundo + duracion)

            componentes = vista.resumen["componentes"]
            articulaciones = len(vista.resumen["articulaciones"])

            if componentes == 1:
                frase_componentes = "1 componente"
            else:
                frase_componentes = f"{componentes} componentes"
            if articulaciones == 1:
                frase_articulaciones = "1 articulación"
            else:
                frase_articulaciones = f"{articulaciones} articulaciones"

            color_componentes = color_componente(0) if componentes > 0 else TENUE
            color_articulaciones = ROJO if articulaciones > 0 else TENUE

            resultado = VGroup(
                texto(frase_componentes, 28, color_componentes, weight=BOLD),
                texto(frase_articulaciones, 28, color_articulaciones, weight=BOLD),
                texto(nota, 20, TENUE),
            ).arrange(DOWN, buff=0.16)
            resultado.move_to([x, -1.85, 0])
            self.play(FadeIn(resultado, shift=UP * 0.2), run_time=0.6)

        self.esperar_hasta(39.4)
        self.limpiar(0.6)

    def mostrar_complejidad(self):
        traza = leer_traza("principal")
        n = traza[0]["n"]
        m = len(traza[0]["aristas"])
        operaciones = traza[-1]["ops"]

        equivalencias = {n: "= V", 2 * m: "= 2E", m: "= E"}

        contadores = [
            ("vértices visitados", operaciones["visitas"], 41.6),
            ("adyacencias revisadas", operaciones["aristas"], 44.2),
            ("aristas que entran a la pila", operaciones["push"], 47.6),
            ("aristas que salen de la pila", operaciones["pop"], 49.6),
        ]

        origen = texto(f"contado por el programa en nuestro grafo:  V = {n},  E = {m}", 22, TENUE)
        origen.move_to([-6.6, 2.5, 0], aligned_edge=LEFT)
        self.play(*self.cambiar_rotulo("arriba", "¿Cuánto cuesta?"), FadeIn(origen), run_time=0.8)

        for orden, (nombre, valor, segundo) in enumerate(contadores):
            y = 1.65 - orden * 0.8
            fila = VGroup(
                texto(nombre, 26).move_to([-6.6, y, 0], aligned_edge=LEFT),
                texto(str(valor), 34, CIAN, fuente=FUENTE_CODIGO, weight=BOLD).move_to([-1.75, y, 0], aligned_edge=RIGHT),
                texto(equivalencias.get(valor, ""), 30, weight=BOLD).move_to([-1.5, y, 0], aligned_edge=LEFT),
            )
            self.esperar_hasta(segundo)
            self.play(FadeIn(fila, shift=RIGHT * 0.3), run_time=0.6)

        self.esperar_hasta(51.6)
        orden_total = VGroup(
            texto("O(V + E)", 60, VERDE, fuente=FUENTE_CODIGO, weight=BOLD),
            texto("en tiempo y en memoria", 24, TENUE),
        ).arrange(DOWN, buff=0.2)
        orden_total.move_to([-3.9, -2.2, 0])
        self.play(FadeIn(orden_total, scale=0.7), run_time=0.8)

        mediciones = leer_mediciones()
        ultima = mediciones[-1]
        x_origen = 1.7
        y_origen = -2.55
        ancho = 4.9
        alto = 4.3
        x_maximo = ultima["n"] + ultima["m"]
        y_maximo = ultima["ingenuo"]

        def punto(x, y):
            return np.array([x_origen + ancho * x / x_maximo, y_origen + alto * y / y_maximo, 0])

        puntos_ingenuo = [punto(0, 0)]
        puntos_dfs = [punto(0, 0)]
        for medicion in mediciones:
            tam = medicion["n"] + medicion["m"]
            puntos_ingenuo.append(punto(tam, medicion["ingenuo"]))
            puntos_dfs.append(punto(tam, medicion["biconexas"]))

        ejes = VGroup(
            Line([x_origen, y_origen, 0], [x_origen + ancho + 0.2, y_origen, 0]),
            Line([x_origen, y_origen, 0], [x_origen, y_origen + alto + 0.2, 0]),
        ).set_stroke(TENUE, 2.5)
        nombre_x = texto("tamaño del grafo  (V + E)", 20, TENUE).next_to(ejes[0], DOWN, buff=0.15).align_to(ejes[0], RIGHT)
        nombre_y = texto("operaciones", 20, TENUE).move_to([x_origen + 0.15, y_origen + alto + 0.45, 0], aligned_edge=LEFT)

        curva_ingenuo = VMobject().set_points_smoothly(puntos_ingenuo).set_stroke(ROJO, 6)
        curva_dfs = VMobject().set_points_as_corners(puntos_dfs).set_stroke(VERDE, 6)

        rotulo_ingenuo = VGroup(
            texto("método ingenuo", 24, ROJO, weight=BOLD),
            texto(con_separador_de_miles(ultima["ingenuo"]) + " operaciones", 20, TENUE),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        rotulo_ingenuo.move_to([x_origen + 0.5, y_origen + alto * 0.62, 0], aligned_edge=LEFT)

        rotulo_dfs = VGroup(
            texto("un solo DFS", 24, VERDE, weight=BOLD),
            texto(con_separador_de_miles(ultima["biconexas"]) + " operaciones", 20, TENUE),
        ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        rotulo_dfs.move_to([x_origen + ancho * 0.5, y_origen + 0.55, 0], aligned_edge=LEFT)

        veces = round(ultima["ingenuo"] / ultima["biconexas"])
        comparacion = texto(f"≈ {veces} veces menos trabajo\ncuando V = {ultima['n']}", 22, BLANCO, line_spacing=0.9)
        comparacion.move_to([x_origen + 0.5, y_origen + alto * 0.88, 0], aligned_edge=LEFT)

        self.esperar_hasta(54.6)
        self.play(Create(ejes), FadeIn(nombre_x), FadeIn(nombre_y), run_time=0.8)
        self.play(Create(curva_ingenuo), FadeIn(rotulo_ingenuo), run_time=1.6)
        self.play(Create(curva_dfs), FadeIn(rotulo_dfs), run_time=1.2)
        self.play(FadeIn(comparacion, shift=UP * 0.2), run_time=0.6)
        self.esperar_hasta(61.4)
        self.limpiar(0.6)

    def mostrar_block_cut_tree(self):
        traza = leer_traza("principal")
        vista = VistaGrafo(
            self, traza, POSICIONES["principal"],
            centro=UP * 0.1, escala=1.45, radio=0.36, con_etiquetas=False, tam_numero=30,
        )
        vista.mostrar_resultado()
        articulaciones = vista.resumen["articulaciones"]

        self.play(FadeIn(vista.todo), *self.cambiar_rotulo("arriba", "Un paso más allá: el block-cut tree"), run_time=1.2)
        self.esperar_hasta(65.2)

        animaciones = []
        uniones = []
        for evento in vista.eventos:
            if evento["ev"] != "componente":
                continue
            numero = evento["id"]
            vertices = vista.vertices_de(evento)
            centro = sum(vista.posicion[v] for v in vertices) / len(vertices)

            bloque = RoundedRectangle(width=0.74, height=0.74, corner_radius=0.16)
            bloque.set_fill(vista.color_de_componente[numero], 1)
            bloque.set_stroke(WHITE, 2.5)
            bloque.move_to(centro)
            bloque.set_z_index(3)
            nombre = texto(f"B{numero + 1}", 24, FONDO, weight=BOLD).move_to(centro)
            nombre.set_z_index(4)

            animaciones.append(ReplacementTransform(vista.contorno[numero], bloque))
            animaciones.append(FadeIn(nombre))
            for a, b in evento["aristas"]:
                animaciones.append(FadeOut(vista.linea[frozenset((a, b))]))

            for v in vertices:
                if v in articulaciones:
                    union = Line(centro, vista.posicion[v], color=BLANCO, stroke_width=5)
                    union.set_z_index(1)
                    uniones.append(union)
                else:
                    animaciones.append(vista.circulo[v].animate.move_to(centro).scale(0.2).set_opacity(0))
                    animaciones.append(vista.numero[v].animate.move_to(centro).scale(0.2).set_opacity(0))

        self.play(*animaciones, run_time=2.4)
        self.esperar_hasta(68.4)
        self.play(LaggedStart(*[Create(union) for union in uniones], lag_ratio=0.15), run_time=1.6)

        self.esperar_hasta(70.6)
        mensaje = "cada bloque es una componente; se unen por sus puntos de articulación"
        self.play(*self.cambiar_rotulo("abajo", mensaje), run_time=0.7)

        self.esperar_hasta(75.6)
        mensaje = "de un grafo enredado a su esqueleto, en un solo recorrido"
        self.play(*self.cambiar_rotulo("abajo", mensaje, color=CIAN), run_time=0.7)

        self.esperar_hasta(79.9)
        self.limpiar(0.6)

    def mostrar_creditos(self):
        titulo = texto("Componentes biconexas", 56, weight=BOLD).move_to(UP * 1.9)
        raya = Line(LEFT * 3, RIGHT * 3, color=CIAN, stroke_width=4).next_to(titulo, DOWN, buff=0.3)
        gracias = texto("¡Gracias por ver!", 36, CIAN).next_to(raya, DOWN, buff=0.45)
        nombres = texto(NOMBRES, 30).next_to(gracias, DOWN, buff=0.7)
        nota = texto("Animación generada a partir de nuestra implementación en C++  ·  hecha con Manim", 22, TENUE)
        nota.next_to(nombres, DOWN, buff=0.6)
        curso = texto(CURSO, 22, TENUE).to_edge(DOWN, buff=0.5)

        self.play(Write(titulo), Create(raya), run_time=1.0)
        self.play(FadeIn(gracias, shift=UP * 0.2), FadeIn(nombres), FadeIn(nota), FadeIn(curso), run_time=0.9)
        self.esperar_hasta(88.0)


class Parte1(EscenaBase):
    def construct(self):
        self.parte1()


class Parte2(EscenaBase):
    def construct(self):
        self.parte2()


class Parte3(EscenaBase):
    def construct(self):
        self.parte3()


class Video(EscenaBase):
    def construct(self):
        self.next_section("Parte 1 - Leonardo Alca")
        self.parte1()
        self.next_section("Parte 2 - Luis Nieva")
        self.parte2()
        self.next_section("Parte 3 - Enrique Zheng")
        self.parte3()
