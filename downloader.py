import os

EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff"}


def cargar_fotos_desde_carpeta(carpeta_origen):
    """
    Lee fotos desde una carpeta local.
    carpeta_origen: ruta a la carpeta con las fotos
    Retorna lista de rutas de archivos de imagen.
    """

    print("\n=== Loader: buscando fotos ===")
    print("Carpeta origen:", carpeta_origen)

    # Validación 1: ruta vacía o None
    if not carpeta_origen:
        print("Error: carpeta_origen está vacía o None")
        return []

    # Validación 2: carpeta no existe
    if not os.path.exists(carpeta_origen):
        print("Error: la carpeta no existe:", carpeta_origen)
        return []

    # Validación 3: no es carpeta
    if not os.path.isdir(carpeta_origen):
        print("Error: la ruta no es una carpeta válida")
        return []

    fotos = []

    try:
        archivos = os.listdir(carpeta_origen)
    except Exception as e:
        print(f"Error leyendo la carpeta: {e}")
        return []

    if len(archivos) == 0:
        print("Carpeta vacía")
        return []

    for archivo in archivos:
        try:
            ruta = os.path.join(carpeta_origen, archivo)

            # Validación 4: ignorar carpetas internas
            if not os.path.isfile(ruta):
                print("Ignorado (no es archivo):", ruta)
                continue

            ext = os.path.splitext(archivo)[1].lower()

            # Validación 5: extensión inválida
            if ext not in EXTENSIONES_VALIDAS:
                print("Ignorado (extensión no válida):", archivo)
                continue

            fotos.append(ruta)
            print("Foto encontrada:", ruta)

        except Exception as e:
            print(f"Error procesando archivo {archivo}: {e}")

    # Validación final importante
    if len(fotos) == 0:
        print("No se encontraron imágenes válidas")
    else:
        print(f"Total de fotos válidas: {len(fotos)}")

    print("=== Loader terminó ===\n")

    return fotos
