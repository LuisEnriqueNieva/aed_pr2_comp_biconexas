# Componentes biconexas

Proyecto Final 2 de CS2023 Algoritmos y Estructuras de Datos (UTEC, 2026-2). Grupo: Leonardo Alca, Luis Nieva, Enrique Zheng.

Programamos el algoritmo de componentes biconexas (DFS con `tin`/`low` y una pila de aristas) en C++, y armamos el video animándolo con Manim a partir de la ejecución real del programa, no a mano.

## Cómo sale la animación

`grafo_biconexas.cpp` tiene el algoritmo. Si lo corres con `--traza`, va imprimiendo línea por línea (en JSON) cada paso que hace el DFS: cuándo visita un nodo, cuándo apila una arista, cuándo actualiza `low`, cuándo saca una componente de la pila, etc. El script de Manim (`animacion/biconexas.py`, con ayuda de los otros archivos de esa carpeta) lee esas líneas y dibuja justo eso. Si cambias el grafo de entrada o el algoritmo, el video cambia solo, sin tocar las escenas.

## Qué hay en cada carpeta

- `grafo_biconexas.cpp`: el algoritmo, con los modos `--traza`, `--verificar` y `--bench`.
- `instancias/`: los grafos de entrada que usamos (`n m` y luego las aristas `u v`).
- `animacion/`: las escenas de Manim y los archivos que usan para dibujar el grafo, el código, la pila y las componentes.
- `video/`: el video ya renderizado.
- `informe/`: el informe en LaTeX.

## Para compilar y correr el algoritmo

Hace falta g++ con C++17 (cualquier GCC moderno sirve) y Python 3.10+ con Manim (`pip install manim`).

```bash
g++ -std=c++17 -O2 -o grafo_biconexas grafo_biconexas.cpp
./grafo_biconexas
```

Otros modos:

```bash
./grafo_biconexas --traza instancias/principal.txt
./grafo_biconexas --verificar 30000
./grafo_biconexas --bench
```

## Para generar el video completo

```bash
python -m venv .venv
.venv\Scripts\pip install manim
.venv\Scripts\python -m manim -qh animacion/biconexas.py Video
```

Queda en `media/videos/biconexas/1080p60/Video.mp4`. El script compila el `.cpp` solo si hace falta (o si está desactualizado). En Linux/Mac es `.venv/bin/` en vez de `.venv\Scripts\`.

## El algoritmo, resumido

`tin[u]` es el momento en que el DFS descubre a `u`. `low[u]` es el `tin` más antiguo al que puede llegar el subárbol de `u` usando como mucho una arista de retroceso. Cada arista se apila al recorrerla, y cuando se vuelve de un hijo `v` al padre `u` y `low[v] >= tin[u]`, se desapila hasta `(u, v)`: eso es una componente biconexa, y `u` queda marcado como punto de articulación (la raíz es la excepción: solo es articulación si tuvo más de un hijo en el DFS).

## Complejidad

`O(V + E)`, en tiempo y en memoria. Lo medimos corriendo el propio programa: con V=1500 y E=3000, el algoritmo hace 13 500 operaciones contra 11 250 000 del método que quita cada vértice uno por uno y vuelve a recorrer todo.

## Verificación

`--verificar` genera miles de grafos aleatorios chicos y revisa que los puntos de articulación y las componentes coincidan con un método de fuerza bruta aparte. Probamos 30 000 y coincidieron todos.

## Qué no cubre

Asume grafos simples (sin aristas repetidas). Con aristas paralelas los puntos de articulación siguen saliendo bien, pero la arista duplicada hacia el padre no queda listada en su componente. Un nodo solo no genera ninguna componente, porque reportamos las componentes como conjuntos de aristas.
