import os
import sys
import clip
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from PIL import Image
from tqdm import tqdm
import json
import torchvision.transforms as T

# ─────────────────────────────
# CONFIGURACIÓN DINÁMICA
# ─────────────────────────────


def obtener_config(tipo, subtipo=None):
    base = "assets"

    if tipo == "cubiertas":
        if not subtipo:
            raise ValueError("Debes indicar subtipo para cubiertas")

        sufijo = f"{tipo}_{subtipo}"
        carpeta = f"fotos_{tipo}_{subtipo}"
    else:
        sufijo = tipo
        carpeta = f"fotos_{tipo}"

    return {
        "carpeta": carpeta,
        "modelo": os.path.join(base, f"modelo_{sufijo}.pt"),
        "clases": os.path.join(base, f"clases_{sufijo}.json"),
    }


# ─────────────────────────────
# DATASET
# ─────────────────────────────


class DatasetObras(Dataset):
    def __init__(self, carpeta, preprocess):
        self.datos = []

        self.clases = sorted(
            [d for d in os.listdir(carpeta) if os.path.isdir(os.path.join(carpeta, d))]
        )

        self.clase_a_idx = {c: i for i, c in enumerate(self.clases)}

        for clase in self.clases:
            carpeta_clase = os.path.join(carpeta, clase)

            for archivo in os.listdir(carpeta_clase):
                ext = os.path.splitext(archivo)[1].lower()

                if ext in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                    ruta = os.path.join(carpeta_clase, archivo)
                    self.datos.append((ruta, self.clase_a_idx[clase]))

        print(f"\nDataset cargado:")
        print(f"Total fotos: {len(self.datos)}")
        print(f"Clases: {len(self.clases)}")

        for clase in self.clases:
            cantidad = sum(1 for _, idx in self.datos if idx == self.clase_a_idx[clase])
            print(f"  - {clase}: {cantidad}")

        self.preprocess = preprocess

    def __len__(self):
        return len(self.datos)

    def __getitem__(self, idx):
        ruta, etiqueta = self.datos[idx]

        try:
            img = self.preprocess(Image.open(ruta).convert("RGB"))
        except Exception as e:
            print(f"[WARN] Imagen corrupta: {ruta}")
            return self.__getitem__((idx + 1) % len(self.datos))

        return img, etiqueta


# ─────────────────────────────
# MODELO
# ─────────────────────────────


class ClasificadorObras(nn.Module):
    def __init__(self, input_dim, num_clases):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_clases),
        )

    def forward(self, x):
        return self.fc(x)


# ─────────────────────────────
# ENTRENAMIENTO
# ─────────────────────────────


def entrenar(tipo, subtipo=None):

    print(">>> INICIANDO ENTRENAMIENTO")

    config = obtener_config(tipo, subtipo)

    CARPETA = config["carpeta"]
    MODELO_SALIDA = config["modelo"]
    CLASES_SALIDA = config["clases"]

    print("\n" + "=" * 50)
    print(f"Entrenando modelo: {tipo} {subtipo if subtipo else ''}")
    print("=" * 50)

    if not os.path.exists(CARPETA):
        print(f"No existe la carpeta: {CARPETA}")
        return

    os.makedirs("assets", exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Usando: {device.upper()}")

    print("Cargando CLIP...")
    clip_model, preprocess = clip.load("ViT-B/32", device=device)
    clip_model.eval()

    # AUGMENT SIN ROMPER CLIP
    augment = T.Compose(
        [
            T.RandomHorizontalFlip(),
            T.RandomRotation(10),
            T.ColorJitter(brightness=0.2, contrast=0.2),
        ]
    )

    dataset = DatasetObras(CARPETA, lambda img: preprocess(augment(img)))

    if len(dataset) == 0:
        print("No hay imágenes")
        return

    # SPLIT TRAIN / VAL
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

    num_clases = len(dataset.clases)
    feature_dim = 512

    modelo = ClasificadorObras(feature_dim, num_clases).to(device)

    criterio = nn.CrossEntropyLoss()
    optimizador = torch.optim.Adam(modelo.parameters(), lr=1e-4)

    EPOCAS = 40
    mejor_precision = 0

    print("\nEntrenando...\n")

    for epoca in range(EPOCAS):

        modelo.train()
        correctas = 0
        total = 0
        perdida_total = 0

        loop = tqdm(train_loader, desc=f"Epoca {epoca+1}/{EPOCAS}", leave=True)

        for imagenes, etiquetas in loop:

            imagenes = imagenes.to(device)
            etiquetas = etiquetas.to(device)

            with torch.no_grad():
                features = clip_model.encode_image(imagenes).float()
                features /= features.norm(dim=-1, keepdim=True)

            optimizador.zero_grad()
            salidas = modelo(features)

            loss = criterio(salidas, etiquetas)
            loss.backward()
            optimizador.step()

            perdida_total += loss.item()

            _, preds = salidas.max(1)
            correctas += preds.eq(etiquetas).sum().item()
            total += etiquetas.size(0)

            precision_actual = 100 * correctas / total
            loop.set_postfix(
                {"loss": f"{loss.item():.4f}", "acc": f"{precision_actual:.2f}%"}
            )

        # RESUMEN ENTRENAMIENTO
        precision = 100 * correctas / total
        perdida_prom = perdida_total / len(train_loader)

        print(
            f"Epoca {epoca+1}/{EPOCAS}: 100% | "
            f"Perdida: {perdida_prom:.4f} | "
            f"Precision: {precision:.2f}%"
        )

        # VALIDACIÓN REAL
        modelo.eval()
        correctas_val = 0
        total_val = 0

        with torch.no_grad():
            for imgs, labels in val_loader:

                imgs = imgs.to(device)
                labels = labels.to(device)

                features = clip_model.encode_image(imgs).float()
                features /= features.norm(dim=-1, keepdim=True)

                salidas = modelo(features)
                _, preds = salidas.max(1)

                correctas_val += preds.eq(labels).sum().item()
                total_val += labels.size(0)

        precision_val = 100 * correctas_val / total_val

        print(f"Validación: {precision_val:.2f}%")

        # GUARDAR MEJOR MODELO (VALIDACIÓN)
        if precision_val > mejor_precision:
            mejor_precision = precision_val

            torch.save(
                {
                    "clasificador": modelo.state_dict(),
                    "clases": dataset.clases,
                    "feature_dim": feature_dim,
                    "num_clases": num_clases,
                },
                MODELO_SALIDA,
            )

    with open(CLASES_SALIDA, "w", encoding="utf-8") as f:
        json.dump(dataset.clases, f, indent=2)

    print("\nEntrenamiento terminado")
    print(f"Mejor precision validación: {mejor_precision:.2f}%")
    print(f"Modelo guardado en: {MODELO_SALIDA}")
    print(f"Clases guardadas en: {CLASES_SALIDA}")


# ─────────────────────────────
# MAIN
# ─────────────────────────────

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso:")
        print("python entrenar.py fachadas")
        print("python entrenar.py cubiertas plana")
        sys.exit()

    tipo = sys.argv[1]
    subtipo = sys.argv[2] if len(sys.argv) > 2 else None

    entrenar(tipo, subtipo)
