import sys
from pathlib import Path

import av

ruta_video = sys.argv[1]
carpeta = Path(sys.argv[2])
segundos = sorted(float(valor) for valor in sys.argv[3:])

carpeta.mkdir(parents=True, exist_ok=True)

with av.open(ruta_video) as video:
    pista = video.streams.video[0]
    duracion = float(pista.duration * pista.time_base)
    print(f"duracion: {duracion:.2f} s, {pista.width}x{pista.height}, {float(pista.average_rate):.0f} fps")

    pendientes = list(segundos)
    for cuadro in video.decode(pista):
        if not pendientes:
            break
        if cuadro.time >= pendientes[0]:
            segundo = pendientes.pop(0)
            cuadro.to_image().save(carpeta / f"t{segundo:06.1f}.png")
