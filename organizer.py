import os
import shutil
import traceback


def organizar_fotos(resultados, destino):
    """
    resultados: lista de diccionarios con:
        {
            "foto": ruta de la foto original,
            "conjunto": nombre del conjunto,
            "actividad": actividad detectada,
            "probabilidad": porcentaje de confianza
        }
    destino: carpeta raíz donde se organizarán las fotos
    """

    print("\n=== Organizador: iniciando ===")
    print("Destino raíz:", destino)

    # Validación 1
    if not resultados:
        print("No hay resultados para organizar")
        return

    if not destino:
        print("Destino vacío")
        return

    try:
        os.makedirs(destino, exist_ok=True)
    except Exception as e:
        print("No se pudo crear carpeta raíz:", e)
        return

    total_ok = 0
    total_error = 0

    for i, r in enumerate(resultados):
        print(f"\n [{i+1}/{len(resultados)}] Procesando:")

        try:
            print("Datos:", r)

            # Validación 2: estructura
            if not isinstance(r, dict):
                print("Resultado inválido (no es dict)")
                total_error += 1
                continue

            if "foto" not in r or "actividad" not in r or "probabilidad" not in r:
                print("Faltan claves en resultado")
                total_error += 1
                continue

            foto = r["foto"]
            conjunto = r.get("conjunto", "SinNombre")
            prob = r["probabilidad"]

            # Validación 3: probabilidad
            try:
                prob = float(prob)
            except:
                print("Probabilidad inválida, usando 0")
                prob = 0

            # Regla principal
            actividad = r["actividad"] if prob >= 20 else "Revisar"

            # Limpiar nombres inválidos de Windows
            conjunto = limpiar_nombre(conjunto)
            actividad = limpiar_nombre(actividad)

            carpeta_destino = os.path.join(destino, conjunto, actividad)

            try:
                os.makedirs(carpeta_destino, exist_ok=True)
                print("Carpeta lista:", carpeta_destino)
            except Exception as e:
                print("Error creando carpeta:", e)
                total_error += 1
                continue

            # Validar archivo
            if not os.path.exists(foto):
                print("No existe la foto:", foto)
                total_error += 1
                continue

            nombre_archivo = os.path.basename(foto)
            destino_foto = os.path.join(carpeta_destino, nombre_archivo)

            # Evitar sobrescribir
            destino_foto = evitar_duplicados(destino_foto)

            try:
                shutil.copy2(foto, destino_foto)
                print("Copiada:", destino_foto)
                total_ok += 1
            except Exception as e:
                print("Error copiando archivo:", e)
                total_error += 1

        except Exception as e:
            print("Error general en item:", e)
            traceback.print_exc()
            total_error += 1

    print("\n=== RESUMEN ===")
    print(f"Copiadas: {total_ok}")
    print(f"Errores: {total_error}")
    print("=== Organizador terminó ===\n")


# ─────────────────────────────
# HELPERS
# ─────────────────────────────


def limpiar_nombre(nombre):
    "Elimina caracteres inválidos para carpetas"
    caracteres_invalidos = '<>:"/\\|?*'
    for c in caracteres_invalidos:
        nombre = nombre.replace(c, "_")
    return nombre.strip()


def evitar_duplicados(ruta):
    "Evita sobrescribir archivos"
    if not os.path.exists(ruta):
        return ruta

    base, ext = os.path.splitext(ruta)
    i = 1

    while True:
        nueva_ruta = f"{base}_{i}{ext}"
        if not os.path.exists(nueva_ruta):
            return nueva_ruta
        i += 1
