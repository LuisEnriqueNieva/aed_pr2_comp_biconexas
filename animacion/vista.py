import numpy as np
from manim import (
    BOLD,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    WHITE,
    AnimationGroup,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    Line,
    RoundedRectangle,
    Transform,
    VGroup,
)

from estilo import (
    AMARILLO,
    BLANCO,
    BORDE,
    CIAN,
    CIAN_OSCURO,
    FONDO,
    FUENTE_CODIGO,
    GRIS,
    NODO,
    PANEL,
    ROJO,
    TENUE,
    VERDE,
    color_componente,
    texto,
)
from paneles import contorno

PESO = {
    "inicio": 1.0,
    "avance": 1.0,
    "retroceso": 1.6,
    "retorno": 1.3,
    "componente": 2.6,
    "fin": 1.2,
}

COLORES_AL_SEPARAR = [CIAN, AMARILLO, VERDE, "#d2a8ff"]


class VistaGrafo:
    def __init__(self, escena, traza, posiciones, centro=ORIGIN, escala=1.0, radio=0.3,
                 con_etiquetas=True, tam_numero=26, codigo=None, pila=None,
                 lugar_estado=None, ancho_estado=7.85):
        self.escena = escena
        self.codigo = codigo
        self.pila = pila
        self.lugar_estado = lugar_estado
        self.ancho_estado = ancho_estado
        self.radio = radio
        self.con_etiquetas = con_etiquetas

        self.n = traza[0]["n"]
        self.aristas = [tuple(arista) for arista in traza[0]["aristas"]]
        self.eventos = traza[1:-1]
        self.resumen = traza[-1]

        centro = np.array(centro, dtype=float)
        self.posicion = {}
        self.lado_etiqueta = {}
        for v, (x, y) in posiciones.items():
            self.posicion[v] = centro + escala * np.array([x, y, 0.0])
            self.lado_etiqueta[v] = UP if y >= 0 else DOWN

        self.circulo = {}
        self.numero = {}
        for v in range(1, self.n + 1):
            circulo = Circle(radius=radio)
            circulo.set_fill(NODO, 1)
            circulo.set_stroke(BLANCO, 3)
            circulo.move_to(self.posicion[v])
            circulo.set_z_index(3)
            self.circulo[v] = circulo

            numero = texto(str(v), tam_numero, weight=BOLD)
            numero.move_to(self.posicion[v])
            numero.set_z_index(4)
            self.numero[v] = numero

        self.linea = {}
        for a, b in self.aristas:
            linea = Line(self.posicion[a], self.posicion[b], color=GRIS, stroke_width=4)
            linea.set_z_index(1)
            self.linea[frozenset((a, b))] = linea

        self.todo = VGroup(*self.linea.values(), *self.circulo.values(), *self.numero.values())

        self.tin = {}
        self.low = {}
        self.etiqueta = {}
        self.linea_retroceso = {}
        self.anillo = {}
        self.contorno = {}
        self.color_de_componente = {}
        self.caminante = None
        self.texto_estado = None
        self.cambios_al_quitar = []

        self.componentes_de = {}
        for v in range(1, self.n + 1):
            self.componentes_de[v] = []
        for evento in self.eventos:
            if evento["ev"] == "componente":
                for v in self.vertices_de(evento):
                    self.componentes_de[v].append(evento["id"])

    def vertices_de(self, componente):
        vertices = set()
        for a, b in componente["aristas"]:
            vertices.add(a)
            vertices.add(b)
        return sorted(vertices)

    def aparecer(self):
        nodos = []
        for v in self.circulo:
            nodos.append(AnimationGroup(FadeIn(self.circulo[v], scale=0.4), FadeIn(self.numero[v], scale=0.4)))
        animaciones = [LaggedStart(*nodos, lag_ratio=0.08)]

        if self.linea:
            lineas = [Create(linea) for linea in self.linea.values()]
            animaciones.append(LaggedStart(*lineas, lag_ratio=0.08))
        return AnimationGroup(*animaciones)

    def crear_etiqueta(self, v, tin, low):
        valor_tin = texto(str(tin), 20, BLANCO, fuente=FUENTE_CODIGO)
        punto = texto("·", 20, TENUE, fuente=FUENTE_CODIGO)
        valor_low = texto(str(low), 20, AMARILLO, fuente=FUENTE_CODIGO, weight=BOLD)
        valores = VGroup(valor_tin, punto, valor_low).arrange(RIGHT, buff=0.09)

        fondo = RoundedRectangle(width=valores.width + 0.3, height=0.38, corner_radius=0.19)
        fondo.set_fill(PANEL, 0.96)
        fondo.set_stroke(BORDE, 1.5)

        etiqueta = VGroup(fondo, valores)
        etiqueta.move_to(self.posicion[v] + self.lado_etiqueta[v] * (self.radio + 0.33))
        etiqueta.set_z_index(5)
        return etiqueta

    def pintar_nodo(self, v, estado):
        circulo = self.circulo[v]
        numero = self.numero[v]
        if estado == "activo":
            return [circulo.animate.set_fill(CIAN, 1).set_stroke(CIAN, 3), numero.animate.set_color(FONDO)]
        if estado == "en_camino":
            return [circulo.animate.set_fill("#12343a", 1).set_stroke(CIAN, 3), numero.animate.set_color(BLANCO)]
        return [circulo.animate.set_fill(NODO, 1).set_stroke("#aab4c0", 3), numero.animate.set_color(BLANCO)]

    def mostrar_estado(self, mensaje, color=BLANCO, resaltar=None):
        if self.lugar_estado is None:
            return []

        nuevo = texto(mensaje, 23, color, t2c=resaltar or {})
        if nuevo.width > self.ancho_estado:
            nuevo.scale(self.ancho_estado / nuevo.width)
        nuevo.move_to(self.lugar_estado, aligned_edge=LEFT)
        nuevo.set_z_index(12)

        if self.texto_estado is not None:
            self.escena.remove(self.texto_estado)
        self.texto_estado = nuevo
        return [FadeIn(nuevo)]

    def marcar_codigo(self, fragmento):
        if self.codigo is None:
            return []
        return [self.codigo.ir_a(fragmento)]

    def cambiar_low(self, u, valor):
        self.low[u] = valor
        if not self.con_etiquetas:
            return []
        nueva = self.crear_etiqueta(u, self.tin[u], valor)
        return [Transform(self.etiqueta[u], nueva)]

    def reproducir_paso(self, animaciones, duracion):
        if animaciones:
            self.escena.play(*animaciones, run_time=duracion)
        else:
            self.escena.wait(duracion)


    def animar_inicio(self, evento, duracion):
        u = evento["u"]
        self.tin[u] = evento["tin"]
        self.low[u] = evento["tin"]

        halo = Circle(radius=0.2)
        halo.set_fill(WHITE, 0.25)
        halo.set_stroke(width=0)
        self.caminante = VGroup(halo, Dot(radius=0.085, color=WHITE))
        self.caminante.set_z_index(3.5)
        self.caminante.move_to(self.posicion[u])

        animaciones = self.pintar_nodo(u, "activo")
        animaciones += self.marcar_codigo("tin[u] = low[u] = temporizador++")
        animaciones += self.mostrar_estado(
            f"el DFS empieza en el nodo {u}:  tin[{u}] = low[{u}] = {evento['tin']}"
        )
        if self.con_etiquetas:
            self.etiqueta[u] = self.crear_etiqueta(u, evento["tin"], evento["tin"])
            animaciones.append(FadeIn(self.etiqueta[u], scale=0.5))
        animaciones.append(FadeIn(self.caminante))
        self.reproducir_paso(animaciones, duracion)

    def animar_avance(self, evento, visita, duracion):
        u = evento["u"]
        v = evento["v"]
        tin = visita["tin"]
        self.tin[v] = tin
        self.low[v] = tin
        clave = frozenset((u, v))
        medio = (self.posicion[u] + self.posicion[v]) / 2

        animaciones = self.pintar_nodo(u, "en_camino")
        animaciones += self.marcar_codigo("pilaAristas.push({u, v});")
        animaciones.append(self.linea[clave].animate.set_stroke(CIAN, 7))
        animaciones.append(self.caminante.animate.move_to(self.posicion[v]))
        animaciones += self.mostrar_estado(
            f"avanza {u} → {v}:  apila ({u},{v}),  tin[{v}] = low[{v}] = {tin}"
        )
        if self.pila is not None:
            animaciones.append(self.pila.apilar(u, v, CIAN, medio))
        self.reproducir_paso(animaciones, 0.55 * duracion)

        animaciones = self.pintar_nodo(v, "activo")
        animaciones += self.marcar_codigo("tin[u] = low[u] = temporizador++")
        if self.con_etiquetas:
            self.etiqueta[v] = self.crear_etiqueta(v, tin, tin)
            animaciones.append(FadeIn(self.etiqueta[v], scale=0.5))
        self.reproducir_paso(animaciones, 0.45 * duracion)

    def animar_retroceso(self, evento, duracion):
        u = evento["u"]
        v = evento["v"]
        clave = frozenset((u, v))
        medio = (self.posicion[u] + self.posicion[v]) / 2

        punteada = DashedLine(self.posicion[u], self.posicion[v], dash_length=0.13, color=AMARILLO, stroke_width=5)
        punteada.set_z_index(2)
        self.linea_retroceso[clave] = punteada

        chispa = Dot(radius=0.09, color=AMARILLO)
        chispa.move_to(self.posicion[u])
        chispa.set_z_index(6)

        animaciones = [
            Create(punteada),
            self.linea[clave].animate.set_stroke(opacity=0.0),
            chispa.animate.move_to(self.posicion[v]),
        ]
        animaciones += self.marcar_codigo("else if (tin[v] < tin[u])")
        animaciones += self.mostrar_estado(
            f"{u} → {v} ya estaba visitado: arista de retroceso",
            resaltar={"arista de retroceso": AMARILLO},
        )
        if self.pila is not None:
            animaciones.append(self.pila.apilar(u, v, AMARILLO, medio))
        self.reproducir_paso(animaciones, 0.5 * duracion)

        low_anterior = self.low[u]
        low_nuevo = evento["low_u"]
        animaciones = self.cambiar_low(u, low_nuevo)
        animaciones += self.marcar_codigo("low[u] = min(low[u], tin[v]);")
        animaciones += self.mostrar_estado(
            f"low[{u}] = min({low_anterior}, tin[{v}] = {evento['tin_v']}) = {low_nuevo}",
            resaltar={f"= {low_nuevo}": AMARILLO},
        )
        animaciones.append(FadeOut(chispa, scale=2.5))
        animaciones.append(Flash(self.posicion[v], color=AMARILLO, line_length=0.18, flash_radius=self.radio + 0.1))
        if self.con_etiquetas:
            animaciones.append(Indicate(self.etiqueta[u], color=AMARILLO, scale_factor=1.3))
        self.reproducir_paso(animaciones, 0.5 * duracion)

    def animar_retorno(self, evento, duracion):
        u = evento["u"]
        v = evento["v"]
        clave = frozenset((u, v))
        low_anterior = self.low[u]

        animaciones = self.pintar_nodo(v, "terminado")
        animaciones += self.pintar_nodo(u, "activo")
        animaciones += self.marcar_codigo("low[u] = min(low[u], low[v]);")
        animaciones.append(self.caminante.animate.move_to(self.posicion[u]))
        animaciones.append(self.linea[clave].animate.set_stroke(CIAN_OSCURO, 6))
        animaciones += self.cambiar_low(u, evento["low_u"])
        animaciones += self.mostrar_estado(
            f"regresa a {u}:  low[{u}] = min({low_anterior}, low[{v}] = {evento['low_v']}) = {evento['low_u']}"
        )
        self.reproducir_paso(animaciones, 0.5 * duracion)

        if evento["cumple"]:
            respuesta = "sí: se cierra una componente"
            color = VERDE
        else:
            respuesta = "no: sigue regresando"
            color = TENUE

        animaciones = self.marcar_codigo("if (low[v] >= tin[u])")
        animaciones += self.mostrar_estado(
            f"¿low[{v}] = {evento['low_v']}  ≥  tin[{u}] = {evento['tin_u']}?   {respuesta}",
            resaltar={respuesta: color},
        )
        if self.con_etiquetas:
            animaciones.append(Indicate(self.etiqueta[v], color=color, scale_factor=1.25))
            animaciones.append(Indicate(self.etiqueta[u], color=color, scale_factor=1.25))
        self.reproducir_paso(animaciones, 0.5 * duracion)

    def colorear_componente(self, componente, incluir_u=False):
        numero = componente["id"]
        color = color_componente(numero)
        self.color_de_componente[numero] = color
        vertices = self.vertices_de(componente)

        mancha = contorno([self.posicion[v] for v in vertices], self.radio + 0.24, color)
        self.contorno[numero] = mancha
        self.todo.add(mancha)

        animaciones = [FadeIn(mancha, scale=0.85)]
        for a, b in componente["aristas"]:
            clave = frozenset((a, b))
            animaciones.append(self.linea[clave].animate.set_stroke(color, 8, 1.0))
            if clave in self.linea_retroceso:
                animaciones.append(FadeOut(self.linea_retroceso.pop(clave)))

        for v in vertices:
            pertenece_a_una = len(self.componentes_de[v]) == 1
            if pertenece_a_una and (v != componente["u"] or incluir_u):
                animaciones.append(self.circulo[v].animate.set_stroke(color, 4))
        return animaciones

    def crear_anillo(self, v):
        anillo = Circle(radius=self.radio + 0.13)
        anillo.set_stroke(ROJO, 5)
        anillo.move_to(self.posicion[v])
        anillo.set_z_index(3)
        self.anillo[v] = anillo
        self.todo.add(anillo)
        return anillo

    def marcar_articulacion(self, v):
        return GrowFromCenter(self.crear_anillo(v))

    def animar_componente(self, evento, duracion):
        u = evento["u"]
        v = evento["v"]
        color = color_componente(evento["id"])
        nombre = f"componente biconexa {evento['id'] + 1}"

        animaciones = self.marcar_codigo("while (pilaAristas.top() != make_pair(u, v))")
        animaciones += self.mostrar_estado(f"desapila hasta ({u},{v}):  {nombre}", resaltar={nombre: color})
        fichas = []
        if self.pila is not None:
            fichas = self.pila.desapilar(len(evento["aristas"]))
            subidas = [ficha.animate.shift(UP * 0.3).set_stroke(color) for ficha in fichas]
            animaciones.append(LaggedStart(*subidas, lag_ratio=0.25))
        self.reproducir_paso(animaciones, 0.35 * duracion)

        animaciones = self.colorear_componente(evento)
        animaciones += self.marcar_codigo("componentesBiconexas.push_back(comp);")
        for ficha, (a, b) in zip(fichas, evento["aristas"]):
            medio = (self.posicion[a] + self.posicion[b]) / 2
            animaciones.append(ficha.animate.move_to(medio).scale(0.3).set_opacity(0))
        self.reproducir_paso(animaciones, 0.4 * duracion)
        for ficha in fichas:
            self.escena.remove(ficha)

        if evento["articulacion"]:
            animaciones = [self.marcar_articulacion(u)]
            animaciones += self.marcar_codigo("if (padre != -1) esArticulacion[u] = true;")
            animaciones += self.mostrar_estado(
                f"{nombre}  ·  el nodo {u} es punto de articulación",
                resaltar={nombre: color, "punto de articulación": ROJO},
            )
            self.reproducir_paso(animaciones, 0.25 * duracion)
        else:
            self.escena.wait(0.25 * duracion)

    def animar_fin_raiz(self, evento, duracion):
        u = evento["u"]
        hijos = evento["hijos"]
        if hijos == 1:
            cuantos = "1 hijo"
        else:
            cuantos = f"{hijos} hijos"

        if evento["articulacion"]:
            conclusion = "sí es punto de articulación"
            color = ROJO
            animaciones = self.pintar_nodo(u, "terminado")
            animaciones.append(self.marcar_articulacion(u))
        else:
            conclusion = "no es articulación"
            color = TENUE
            animaciones = self.pintar_nodo(u, "terminado")
            if len(self.componentes_de[u]) == 1:
                color_borde = self.color_de_componente[self.componentes_de[u][0]]
                animaciones[0] = self.circulo[u].animate.set_fill(NODO, 1).set_stroke(color_borde, 4)

        animaciones += self.marcar_codigo("if (padre == -1 && hijosRaiz > 1)")
        if self.caminante is not None:
            animaciones.append(FadeOut(self.caminante))
            self.caminante = None
        animaciones += self.mostrar_estado(
            f"la raíz {u} tiene {cuantos} en el árbol del DFS:  {conclusion}",
            resaltar={conclusion: color},
        )
        self.reproducir_paso(animaciones, duracion)

    def tipo_de_paso(self, evento):
        if evento["ev"] == "visitar":
            if evento["padre"] == -1:
                return "inicio"
            return None
        if evento["ev"] == "fin_nodo":
            if evento["padre"] == -1:
                return "fin"
            return None
        if evento["ev"] == "arbol":
            return "avance"
        return evento["ev"]

    def peso(self, desde, hasta):
        total = 0
        for evento in self.eventos[desde:hasta]:
            tipo = self.tipo_de_paso(evento)
            if tipo is not None:
                total += PESO[tipo]
        return total

    def reproducir(self, desde, hasta, limite):
        peso_pendiente = self.peso(desde, hasta)

        for indice in range(desde, hasta):
            evento = self.eventos[indice]
            tipo = self.tipo_de_paso(evento)
            if tipo is None:
                continue

            ahora = self.escena.renderer.time - self.escena.inicio_parte
            duracion = (limite - ahora) * PESO[tipo] / peso_pendiente
            duracion = max(0.3, duracion)
            peso_pendiente -= PESO[tipo]

            if tipo == "inicio":
                self.animar_inicio(evento, duracion)
            elif tipo == "avance":
                self.animar_avance(evento, self.eventos[indice + 1], duracion)
            elif tipo == "retroceso":
                self.animar_retroceso(evento, duracion)
            elif tipo == "retorno":
                self.animar_retorno(evento, duracion)
            elif tipo == "componente":
                self.animar_componente(evento, duracion)
            elif tipo == "fin":
                self.animar_fin_raiz(evento, duracion)

    def buscar_evento(self, condicion):
        indice = 0
        while not condicion(self.eventos[indice]):
            indice += 1
        return indice

    def mostrar_resultado(self):
        for evento in self.eventos:
            if evento["ev"] != "componente":
                continue
            numero = evento["id"]
            color = color_componente(numero)
            self.color_de_componente[numero] = color
            vertices = self.vertices_de(evento)

            mancha = contorno([self.posicion[v] for v in vertices], self.radio + 0.24, color)
            self.contorno[numero] = mancha
            self.todo.add(mancha)

            for a, b in evento["aristas"]:
                self.linea[frozenset((a, b))].set_stroke(color, 8)
            for v in vertices:
                if len(self.componentes_de[v]) == 1:
                    self.circulo[v].set_stroke(color, 4)

        for v in self.resumen["articulaciones"]:
            self.crear_anillo(v)

    def quitar_vertice(self, v, grupos=None, separacion=0.0):
        animaciones = [
            self.circulo[v].animate.set_fill(opacity=0.1).set_stroke(opacity=0.15),
            self.numero[v].animate.set_opacity(0.15),
        ]
        self.cambios_al_quitar = [("nodo", v)]

        for clave, linea in self.linea.items():
            if v in clave:
                animaciones.append(linea.animate.set_stroke(opacity=0.08))
                self.cambios_al_quitar.append(("linea", clave))

        if grupos is None or separacion == 0:
            return animaciones

        miembros = {}
        for w in range(1, self.n + 1):
            if w != v:
                miembros.setdefault(grupos[w - 1], []).append(w)

        centros = {}
        for grupo, vertices in miembros.items():
            centros[grupo] = sum(self.posicion[w] for w in vertices) / len(vertices)
        centro_general = sum(centros.values()) / len(centros)

        for orden, grupo in enumerate(sorted(miembros)):
            vertices = miembros[grupo]
            color = COLORES_AL_SEPARAR[orden % len(COLORES_AL_SEPARAR)]
            direccion = centros[grupo] - centro_general
            largo = np.linalg.norm(direccion)
            if largo > 0:
                direccion = direccion / largo
            desplazamiento = separacion * direccion

            for w in vertices:
                animaciones.append(self.circulo[w].animate.shift(desplazamiento).set_stroke(color, 4))
                animaciones.append(self.numero[w].animate.shift(desplazamiento))
                self.cambios_al_quitar.append(("nodo_movido", w, desplazamiento))
            for clave, linea in self.linea.items():
                if clave <= set(vertices):
                    animaciones.append(linea.animate.shift(desplazamiento).set_stroke(color, 5))
                    self.cambios_al_quitar.append(("linea_movida", clave, desplazamiento))
        return animaciones

    def restaurar_vertice(self):
        animaciones = []
        for cambio in self.cambios_al_quitar:
            tipo = cambio[0]
            if tipo == "nodo":
                v = cambio[1]
                animaciones.append(self.circulo[v].animate.set_fill(opacity=1).set_stroke(opacity=1))
                animaciones.append(self.numero[v].animate.set_opacity(1))
            elif tipo == "linea":
                animaciones.append(self.linea[cambio[1]].animate.set_stroke(opacity=1))
            elif tipo == "nodo_movido":
                v = cambio[1]
                regreso = -cambio[2]
                animaciones.append(self.circulo[v].animate.shift(regreso).set_stroke(BLANCO, 3))
                animaciones.append(self.numero[v].animate.shift(regreso))
            elif tipo == "linea_movida":
                animaciones.append(self.linea[cambio[1]].animate.shift(-cambio[2]).set_stroke(GRIS, 4))
        self.cambios_al_quitar = []
        return animaciones
