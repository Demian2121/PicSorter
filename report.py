import os
import json
from collections import defaultdict
import sys


def obtener_ruta_base():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # ruta interna del .exe
    return os.path.abspath(".")


# ─────────────────────────────
# CARGAR DESCRIPCIONES
# ─────────────────────────────
def cargar_descripciones(tipo, subtipo=None):
    base = obtener_ruta_base()
    nombre = "categorias_es.json"

    ruta = os.path.join(base, "assets", nombre)

    print("Cargando descripciones desde:", ruta)

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)

            print("Claves disponibles en JSON:")
            print(list(data.keys()))

            return data

    print("No se encontró el archivo")
    return {}


# ─────────────────────────────
# CREAR info.txt POR CARPETA
# ─────────────────────────────
def guardar_info_carpeta(base_path, conjunto, actividad, fotos, descripciones):
    try:
        ruta = os.path.join(base_path, conjunto, actividad)
        os.makedirs(ruta, exist_ok=True)

        ruta_info = os.path.join(ruta, "info.txt")

        descripcion = descripciones.get(actividad, "Sin descripción disponible")

        contenido = f"""Categoría: {actividad}

Descripción:
{descripcion}

Total fotos: {len(fotos)}

Ejemplos:
"""

        for f in fotos[:5]:
            nombre = os.path.basename(f["foto"])
            contenido += f"- {nombre}\n"

        with open(ruta_info, "w", encoding="utf-8") as f:
            f.write(contenido)

    except Exception as e:
        print(f"[ERROR] guardando info: {e}")


# ─────────────────────────────
# GENERAR REPORTE GENERAL + TXT
# ─────────────────────────────
def generar_reporte(resultados, base_path="salida", tipo="fachadas", subtipo=None):

    print("\n=== Reporte PicSorter ===\n")

    # cargar descripciones en español
    descripciones = cargar_descripciones(tipo, subtipo)

    # agrupar resultados
    agrupado = defaultdict(lambda: defaultdict(list))

    for r in resultados:
        conjunto = r["conjunto"]
        actividad = r["actividad"]
        agrupado[conjunto][actividad].append(r)

    # acumulador para guardar en archivo
    reporte_texto = ""
    reporte_texto += "=== Reporte PicSorter ===\n\n"
    reporte_texto += "Resumen por conjunto y actividad:\n\n"

    print("Resumen por conjunto y actividad:\n")

    # ─────────────────────────────
    # RESUMEN
    # ─────────────────────────────
    for conjunto, actividades in agrupado.items():
        linea = f"Conjunto: {conjunto}"
        print(linea)
        reporte_texto += linea + "\n"

        for actividad, fotos in actividades.items():
            linea = f"  - {actividad}: {len(fotos)} fotos"
            print(linea)
            reporte_texto += linea + "\n"

            # NUEVO: generar info.txt
            guardar_info_carpeta(base_path, conjunto, actividad, fotos, descripciones)

    # ─────────────────────────────
    # DETALLE
    # ─────────────────────────────
    print("\n=== Detalle de fotos clasificadas ===\n")
    reporte_texto += "\n=== Detalle de fotos clasificadas ===\n\n"

    for r in resultados:
        nombre = os.path.basename(r["foto"])
        linea = f"{nombre} -> {r['conjunto']} / {r['actividad']} ({r['probabilidad']}%)"

        print(linea)
        reporte_texto += linea + "\n"

    # ─────────────────────────────
    # GUARDAR REPORTE
    # ─────────────────────────────
    ruta_reporte = os.path.join(base_path, "reporte.txt")

    try:
        os.makedirs(base_path, exist_ok=True)

        with open(ruta_reporte, "w", encoding="utf-8") as f:
            f.write(reporte_texto)

        print(f"\n[OK] Reporte guardado en: {ruta_reporte}")

    except Exception as e:
        print(f"[ERROR] guardando reporte: {e}")
