import tkinter as tk
import sys
import traceback
import os

from menu import iniciar_menu
from classifier import obtener_ruta


def iniciar_app():
    print("\n=== Iniciando PicSorter ===")

    try:
        root = tk.Tk()
        # ICONO PRINCIPAL DE TODA LA APP
        try:
            icon_path = obtener_ruta("assets/PicSorterLiviana.ico")
            print("Icono principal:", icon_path)

            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
                print("Icono aplicado correctamente")
            else:
                print("No se encontró icono")

        except Exception as e:
            print("Error cargando icono:", str(e))
        root.geometry("400x600")
        root.resizable(False, False)

        print("Ventana principal creada")

    except Exception as e:
        print("Error creando la ventana:")
        print(str(e))
        traceback.print_exc()
        input("Presiona ENTER para salir...")
        sys.exit(1)

    try:
        print("Cargando menú principal...")
        iniciar_menu(root)
    except Exception as e:
        print("Error cargando el menú:")
        print(str(e))
        traceback.print_exc()
        input("Presiona ENTER para salir...")
        sys.exit(1)

    try:
        print("Ejecutando mainloop...")
        root.mainloop()
    except Exception as e:
        print("Error en ejecución de la app:")
        print(str(e))
        traceback.print_exc()
        input("Presiona ENTER para salir...")
        sys.exit(1)


# PROTECCIÓN PRINCIPAL
if __name__ == "__main__":
    try:
        iniciar_app()
    except Exception as e:
        print("ERROR CRÍTICO NO CONTROLADO:")
        print(str(e))
        traceback.print_exc()
        input("Presiona ENTER para cerrar...")
        sys.exit(1)
