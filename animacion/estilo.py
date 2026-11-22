from manim import Text, config

FONDO = "#0d1117"
PANEL = "#131a23"
BORDE = "#283241"
NODO = "#161d27"
GRIS = "#4b5666"
TENUE = "#8b98a8"
BLANCO = "#e6edf3"
CIAN = "#39d0d8"
CIAN_OSCURO = "#1c6f78"
AMARILLO = "#ffd866"
ROJO = "#ff6b6b"
VERDE = "#7ee787"

COLORES_COMPONENTE = ["#ffa657", "#7ee787", "#d2a8ff", "#79c0ff", "#ff9bce", "#f2cc60"]

FUENTE = "Segoe UI"
FUENTE_CODIGO = "Consolas"

config.background_color = FONDO


def texto(contenido, tam=28, color=BLANCO, fuente=FUENTE, **opciones):
    return Text(contenido, font=fuente, font_size=tam, color=color, **opciones)


def color_componente(numero):
    return COLORES_COMPONENTE[numero % len(COLORES_COMPONENTE)]
