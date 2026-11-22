import glob
import json
import os
import shutil
import subprocess
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent
FUENTE_CPP = CARPETA / "grafo_biconexas.cpp"

if os.name == "nt":
    EJECUTABLE = CARPETA / "grafo_biconexas.exe"
else:
    EJECUTABLE = CARPETA / "grafo_biconexas"


def buscar_compilador():
    ruta = shutil.which("g++")
    if ruta:
        return ruta

    carpeta_winget = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    candidatos = glob.glob(os.path.join(carpeta_winget, "*WinLibs*", "mingw64", "bin", "g++.exe"))
    if candidatos:
        return candidatos[0]

    raise RuntimeError("No se encontro g++. Compile grafo_biconexas.cpp a mano como indica el README.")


def compilar():
    if EJECUTABLE.exists() and EJECUTABLE.stat().st_mtime >= FUENTE_CPP.stat().st_mtime:
        return

    compilador = buscar_compilador()
    entorno = dict(os.environ)
    entorno["PATH"] = os.path.dirname(compilador) + os.pathsep + entorno.get("PATH", "")
    comando = [compilador, "-std=c++17", "-O2", "-static", "-o", str(EJECUTABLE), str(FUENTE_CPP)]
    subprocess.run(comando, check=True, env=entorno)


def ejecutar(*argumentos):
    compilar()
    resultado = subprocess.run([str(EJECUTABLE), *argumentos], capture_output=True, text=True, check=True)

    lineas = []
    for linea in resultado.stdout.splitlines():
        if linea.strip():
            lineas.append(json.loads(linea))
    return lineas


def leer_traza(nombre):
    return ejecutar("--traza", str(CARPETA / "instancias" / (nombre + ".txt")))


def leer_mediciones():
    return ejecutar("--bench")


def leer_codigo_dfs():
    lineas = FUENTE_CPP.read_text(encoding="utf-8").splitlines()

    inicio = 0
    while "void dfsBiconexas(int u, int padre)" not in lineas[inicio]:
        inicio += 1

    codigo = []
    for linea in lineas[inicio:]:
        contenido = linea.strip()
        if contenido and not contenido.startswith("registrar"):
            espacios = len(linea) - len(linea.lstrip())
            nivel = (espacios - 4) // 4
            codigo.append((nivel, contenido))
        if linea == "    }":
            break
    return codigo
