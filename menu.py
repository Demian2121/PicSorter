import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import traceback
import sys
from gui import cargar_gui


def obtener_ruta(ruta_relativa):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)


def limpiar_ventana(root):
    for widget in root.winfo_children():
        widget.destroy()


def iniciar_menu(root):
    print("\n=== Iniciando menú principal ===")

    try:
        limpiar_ventana(root)
        root.title("PicSorter — Selección")

    except Exception as e:
        print("Error preparando ventana:", e)
        traceback.print_exc()
        return

    # ─────────────────────────────
    # LOGO (blindado)
    # ─────────────────────────────
    try:
        from classifier import obtener_ruta  # si no lo tienes importado
        png_path = obtener_ruta(os.path.join("assets", "PicSorterLiviana.png"))
        print("Buscando logo en:", png_path)

        if os.path.exists(png_path):
            img = Image.open(png_path)
            img = img.resize((180, 180))
            
            logo = ImageTk.PhotoImage(img)

            lbl = tk.Label(root, image=logo)
            lbl.image = logo
            lbl.pack(pady=20)

            print("Logo cargado")
        else:
            print("Logo no encontrado:", png_path)

    except Exception as e:
        print("Error cargando logo:", e)
        traceback.print_exc()

    # ─────────────────────────────
    # TEXTO
    # ─────────────────────────────
    try:
        tk.Label(root, text="Selecciona tipo de proyecto", font=("Arial", 12)).pack(
            pady=10
        )
    except Exception as e:
        print("Error creando label:", e)

    # ─────────────────────────────
    # FUNCIONES
    # ─────────────────────────────
    def abrir_app(tipo, subtipo=None):
        try:
            print(f"Abriendo app: {tipo} | {subtipo}")
            cargar_gui(root, tipo, subtipo)
        except Exception as e:
            print("Error abriendo GUI:", e)
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo abrir la app:\n{e}")

    def cubiertas_menu():
        print("Abriendo menú de cubiertas")

        try:
            ventana = tk.Toplevel(root)
            ventana.title("Tipo de Cubierta")
            ventana.geometry("300x300")

            tk.Label(ventana, text="Selecciona tipo de cubierta").pack(pady=10)

            tk.Button(
                ventana,
                text="Plana",
                width=20,
                command=lambda: abrir_app("cubiertas", "plana"),
            ).pack(pady=5)

            tk.Button(
                ventana,
                text="Teja",
                width=20,
                command=lambda: messagebox.showwarning(
                    "Aviso", "Aún no implementado"
                ),
            ).pack(pady=5)

            tk.Button(
                ventana,
                text="Membrana",
                width=20,
                command=lambda: messagebox.showwarning(
                    "Aviso", "Aún no implementado"
                ),
            ).pack(pady=5)

        except Exception as e:
            print("Error en menú de cubiertas:", e)
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo abrir el menú:\n{e}")

    # ─────────────────────────────
    # BOTONES
    # ─────────────────────────────
    try:
        tk.Button(
            root,
            text="Fachadas",
            width=25,
            height=2,
            command=lambda: abrir_app("fachadas"),
        ).pack(pady=10)

        tk.Button(
            root,
            text="Cubiertas",
            width=25,
            height=2,
            command=cubiertas_menu,
        ).pack(pady=10)

    except Exception as e:
        print("Error creando botones:", e)
        traceback.print_exc()

    print("Menú cargado correctamente")
