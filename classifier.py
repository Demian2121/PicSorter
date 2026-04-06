import torch
import torch.nn as nn
from PIL import Image
import os
import json
import sys


# SOLUCIÓN PARA PYINSTALLER + CLIP
def fix_clip_path():
    try:
        if hasattr(sys, "_MEIPASS"):
            clip_path = os.path.join(sys._MEIPASS, "clip")
            os.environ["CLIP_HOME"] = clip_path
            print(f"[DEBUG] CLIP path corregido: {clip_path}")
    except Exception as e:
        print(f"[ERROR] fix_clip_path: {e}")


fix_clip_path()

# IMPORTANTE: protegido
try:
    import clip
except Exception as e:
    print(f"[ERROR] No se pudo importar CLIP: {e}")
    clip = None


# PRIORIDADES
PRIORIDAD_FACHADAS = [
    "trabajos_en_fachada",
    "danos_fachada",
    "instalaciones_fachada",
    "elementos_fachada",
    "cubierta_visible",
    "fachada_general",
]

PRIORIDAD_CUBIERTAS = [
    "trabajos_en_cubierta",
    "instalaciones_cubierta",
    "estructuras_cubierta",
    "superficie_cubierta",
    "cubierta_general",
]

UMBRAL = 0.25


device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Dispositivo: {device}")

# cargar CLIP seguro
try:
    clip_model, preprocess = clip.load("ViT-B/32", device=device)
    clip_model.eval()
    print("[OK] CLIP cargado correctamente")
except Exception as e:
    print(f"[ERROR] Error cargando CLIP: {e}")
    clip_model = None
    preprocess = None


class ClasificadorObras(nn.Module):
    def __init__(self, input_dim, num_clases):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_clases),
        )

    def forward(self, x):
        return self.fc(x)


def obtener_ruta(ruta_relativa):
    try:
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, ruta_relativa)
        return os.path.join(os.path.abspath("."), ruta_relativa)
    except Exception as e:
        print(f"[ERROR] obtener_ruta: {e}")
        return ruta_relativa


def obtener_rutas(tipo, subtipo=None):
    base = "assets"

    if tipo == "cubiertas" and subtipo:
        sufijo = f"{tipo}_{subtipo}"
    else:
        sufijo = tipo

    rutas = {
        "modelo": os.path.join(base, f"modelo_{sufijo}.pt"),
        "clases": os.path.join(base, f"clases_{sufijo}.json"),
        "categorias": os.path.join(base, f"categorias_{sufijo}.json"),
    }

    print(f"[DEBUG] Rutas generadas: {rutas}")
    return rutas


def cargar_categorias(tipo, subtipo=None):
    rutas = obtener_rutas(tipo, subtipo)

    ruta_categorias = obtener_ruta(rutas["categorias"])
    print("[DEBUG] Buscando categorias en:", ruta_categorias)

    if os.path.exists(ruta_categorias):
        try:
            with open(ruta_categorias, "r", encoding="utf-8") as f:
                data = json.load(f)
                print("[OK] Categorías cargadas:", len(data))
                return data

        except Exception as e:
            print("[ERROR] cargar_categorias:", str(e))
            return {}

    print("[WARN] No existe archivo de categorías")
    return {}


def inicializar_texto(categorias):
    try:
        nombres = []
        todos_los_textos = []
        indices_categoria = []

        for i, (categoria, textos) in enumerate(categorias.items()):
            if isinstance(textos, str):
                textos = [textos]

            for t in textos:
                nombres.append(categoria)
                todos_los_textos.append(t)
                indices_categoria.append(i)

        with torch.no_grad():
            tokens = clip.tokenize(todos_los_textos).to(device)
            features = clip_model.encode_text(tokens)
            features /= features.norm(dim=-1, keepdim=True)

        print("[OK] Texto CLIP inicializado con múltiples prompts")
        return nombres, features, indices_categoria

    except Exception as e:
        print(f"[ERROR] inicializar_texto: {e}")
        return [], None, None


def cargar_modelo(tipo, subtipo=None):
    rutas = obtener_rutas(tipo, subtipo)

    try:
        if os.path.exists(rutas["modelo"]) and os.path.exists(rutas["clases"]):
            print("[INFO] Cargando modelo entrenado...")

            ruta_modelo = obtener_ruta(rutas["modelo"])
            ruta_clases = obtener_ruta(rutas["clases"])

            print("[DEBUG] Modelo en:", ruta_modelo)
            print("[DEBUG] Clases en:", ruta_clases)

            if os.path.exists(ruta_modelo) and os.path.exists(ruta_clases):
                checkpoint = torch.load(ruta_modelo, map_location=device)

            modelo = ClasificadorObras(
                checkpoint["feature_dim"], checkpoint["num_clases"]
            ).to(device)

            modelo.load_state_dict(checkpoint["clasificador"])
            modelo.eval()

            print("[OK] Modelo cargado correctamente")
            return modelo, checkpoint["clases"]

        else:
            print("[WARN] No hay modelo entrenado, usando CLIP")

    except Exception as e:
        print(f"[ERROR] cargar_modelo: {e}")

    return None, None


def clasificar_fotos_por_conjunto(
    fotos, conjunto, progreso=None, tipo="fachadas", subtipo=None
):
    resultados = []

    print(f"[INFO] Iniciando clasificación ({len(fotos)} fotos)")

    modelo, clases = cargar_modelo(tipo, subtipo)

    # seleccionar prioridad según tipo
    if tipo == "fachadas":
        PRIORIDAD = PRIORIDAD_FACHADAS
    elif tipo == "cubiertas":
        PRIORIDAD = PRIORIDAD_CUBIERTAS
    else:
        PRIORIDAD = []

    if modelo is None:
        categorias = cargar_categorias(tipo, subtipo)
        nombres, texto_features, _ = inicializar_texto(categorias)

        if not nombres or texto_features is None:
            print("[ERROR] No se pudo inicializar CLIP texto")
            return []

    # Configurar barra ANTES del loop (una sola vez)
    if progreso:
        try:
            progreso["maximum"] = len(fotos)
            progreso["value"] = 0
        except:
            pass

    for i, foto in enumerate(fotos):

        # Actualizar barra AL INICIO del loop, antes de cualquier continue
        if progreso:
            try:
                progreso["value"] = i + 1
            except:
                pass

        try:
            if not os.path.exists(foto):
                print(f"[WARN] No existe: {foto}")
                continue

            try:
                img = Image.open(foto).convert("RGB")
            except Exception as e:
                print(f"[ERROR] Imagen corrupta: {foto} -> {e}")
                continue

            if preprocess is None:
                print("[ERROR] preprocess no disponible")
                continue

            imagen = preprocess(img).unsqueeze(0).to(device)

            with torch.no_grad():
                features = clip_model.encode_image(imagen).float()
                features /= features.norm(dim=-1, keepdim=True)

            if modelo:
                salidas = modelo(features)
                probs = torch.softmax(salidas, dim=-1)

                valor, idx = probs[0].max(0)
                actividad = clases[idx.item()]
                probabilidad = round(valor.item() * 100, 2)

            else:
                similitudes = (features @ texto_features.T)[0]

                scores_por_categoria = {}

                # Renombrado a j para no sobreescribir el i del loop exterior
                for j, score in enumerate(similitudes):
                    categoria = nombres[j]
                    if categoria not in scores_por_categoria:
                        scores_por_categoria[categoria] = []
                    scores_por_categoria[categoria].append(score.item())

                scores_promedio = {
                    cat: sum(vals) / len(vals)
                    for cat, vals in scores_por_categoria.items()
                }

                print("\n--- DEBUG ---")
                print(f"Imagen: {os.path.basename(foto)}")
                for cat, score in sorted(scores_promedio.items(), key=lambda x: -x[1]):
                    print(f"{cat}: {round(score, 3)}")

                # PRIORIDAD + UMBRAL
                actividad = "Revisar"
                probabilidad = 0

                for cat in PRIORIDAD:
                    if cat in scores_promedio:
                        score = scores_promedio[cat]

                        if score >= UMBRAL:
                            actividad = cat
                            probabilidad = round(score * 100, 2)
                            break

                # si ninguna categoría pasó el umbral → Revisar
                if actividad == "Revisar":
                    print("[INFO] Ninguna categoría supera el umbral → Revisar")

                    # opcional: guardar la mejor probabilidad para análisis
                    mejor_cat = max(scores_promedio, key=scores_promedio.get)
                    probabilidad = round(scores_promedio[mejor_cat] * 100, 2)

            resultados.append(
                {
                    "foto": foto,
                    "conjunto": conjunto,
                    "actividad": actividad,
                    "probabilidad": probabilidad,
                }
            )

        except Exception as e:
            print(f"[ERROR] Fallo procesando {foto}: {e}")
            continue
    if progreso:
        progreso["value"] = len(fotos)
        progreso.update_idletasks()

    print(f"[OK] Clasificación terminada: {len(resultados)} resultados")
    return resultados
