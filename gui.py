import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os
import threading

from downloader import cargar_fotos_desde_carpeta
from classifier import clasificar_fotos_por_conjunto, obtener_ruta
from organizer import organizar_fotos
from report import generar_reporte


def limpiar_ventana(root):
    for widget in root.winfo_children():
        widget.destroy()


def cargar_gui(root, tipo="fachadas", subtipo=None):
    print("\n=== Iniciando GUI ===")
    print(f"Tipo: {tipo} | Subtipo: {subtipo}")

    limpiar_ventana(root)
    root.title(f"PicSorter — {tipo.upper()}")

    top_frame = tk.Frame(root)
    top_frame.pack(fill="x")

    def volver_menu():
        from menu import iniciar_menu

        iniciar_menu(root)

    tk.Button(
        top_frame, text="⬅ Volver", command=volver_menu, bg="#555", fg="white"
    ).pack(side="left", padx=10, pady=5)

    padding = {"padx": 10, "pady": 3}

    try:
        png_path = obtener_ruta(os.path.join("assets", "PicSorterLiviana.png"))
        if os.path.exists(png_path):
            img = Image.open(png_path).resize((200, 200))
            logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(root, image=logo)
            logo_label.image = logo
            logo_label.pack(pady=(10, 0))
    except Exception as e:
        print("Error cargando logo:", e)

    tk.Label(root, text="Nombre del conjunto:").pack(**padding)
    conjunto_entry = tk.Entry(root, width=50)
    conjunto_entry.pack(**padding)

    tk.Label(root, text="Carpeta con fotos:").pack(**padding)
    origen_entry = tk.Entry(root, width=40)
    origen_entry.pack(**padding)

    def seleccionar_origen():
        carpeta = filedialog.askdirectory()
        if carpeta:
            origen_entry.delete(0, tk.END)
            origen_entry.insert(0, carpeta)

    tk.Button(root, text="Seleccionar origen", command=seleccionar_origen).pack()

    tk.Label(root, text="Carpeta destino:").pack(**padding)
    destino_entry = tk.Entry(root, width=40)
    destino_entry.pack(**padding)

    def seleccionar_destino():
        carpeta = filedialog.askdirectory()
        if carpeta:
            destino_entry.delete(0, tk.END)
            destino_entry.insert(0, carpeta)

    tk.Button(root, text="Seleccionar destino", command=seleccionar_destino).pack()

    progreso = ttk.Progressbar(root, length=350)
    progreso.pack(pady=10)

    estado = tk.Label(root, text="", font=("Arial", 10, "bold"))
    estado.pack()

    boton_ejecutar = tk.Button(
        root, text="Ejecutar", bg="#4CAF50", fg="white", width=25
    )
    boton_ejecutar.pack(pady=10)

    # ─────────────────────────────
    # PROCESO EN HILO SEPARADO ← CLAVE
    # ─────────────────────────────
    def proceso_en_hilo(conjunto, origen, destino):
        try:
            fotos = cargar_fotos_desde_carpeta(origen)

            if not fotos:
                root.after(
                    0,
                    lambda: estado.config(
                        text="No se encontraron imágenes", fg="red"
                    ),
                )
                return

            print(f"Fotos a procesar: {len(fotos)}")

            root.after(
                0, lambda: estado.config(text="Clasificando imágenes...", fg="blue")
            )

            resultados = clasificar_fotos_por_conjunto(
                fotos, conjunto, progreso, tipo, subtipo
            )

            if not resultados:
                raise ValueError("Clasificación devolvió lista vacía")

            root.after(
                0, lambda: estado.config(text="Organizando fotos...", fg="blue")
            )

            destino_final = os.path.join(destino, tipo)
            organizar_fotos(resultados, destino_final)

            root.after(
                0, lambda: estado.config(text="Generando reporte...", fg="blue")
            )

            generar_reporte(resultados, destino_final, tipo, subtipo)

            # ← Restaurar botón y mostrar éxito
            root.after(
                0,
                lambda: (
                    progreso.config(value=progreso["maximum"]),
                    progreso.update_idletasks(),
                    estado.config(
                        text="Proceso completado correctamente", fg="green"
                    ),
                    boton_ejecutar.config(state="normal"),
                ),
            )
            print("PROCESO FINALIZADO")

        except Exception as e:
            print("ERROR GENERAL:", str(e))
            root.after(
                0,
                lambda: [
                    estado.config(text=f"Error: {str(e)}", fg="red"),
                    boton_ejecutar.config(state="normal"),
                ],
            )

    def ejecutar():
        conjunto = conjunto_entry.get().strip()
        origen = origen_entry.get().strip()
        destino = destino_entry.get().strip()

        progreso["value"] = 0

        if not conjunto:
            estado.config(text="Ingresa el nombre del conjunto", fg="red")
            return
        if not origen or not os.path.exists(origen):
            estado.config(text="Carpeta origen inválida", fg="red")
            return
        if not destino or not os.path.exists(destino):
            estado.config(text="Carpeta destino inválida", fg="red")
            return

        # Deshabilitar botón mientras corre ← evita doble clic
        boton_ejecutar.config(state="disabled")
        estado.config(text="Iniciando...", fg="gray")

        # Lanzar en hilo separado ← LA LÍNEA MÁS IMPORTANTE
        hilo = threading.Thread(
            target=proceso_en_hilo, args=(conjunto, origen, destino), daemon=True
        )
        hilo.start()

    boton_ejecutar.config(command=ejecutar)
