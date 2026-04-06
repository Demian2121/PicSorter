# PicSorter

PicSorter es una aplicación de escritorio desarrollada en Python para la clasificación automática de imágenes de obras civiles mediante modelos de visión artificial basados en CLIP.

El sistema permite organizar fotografías de inspecciones técnicas (fachadas y cubiertas), clasificarlas por actividad y generar reportes estructurados para facilitar procesos de documentación y control.

---

## Características

* Clasificación automática de imágenes usando modelos de inteligencia artificial
* Soporte para proyectos de fachadas y cubiertas (plana)
* Organización automática de imágenes por actividad detectada
* Generación de reportes en formato texto
* Interfaz gráfica de usuario desarrollada con Tkinter
* Distribución como ejecutable (.exe) sin necesidad de instalar Python

---

## Tecnologías utilizadas

* Python 3.10
* PyTorch
* CLIP (OpenAI)
* Tkinter
* PIL (Pillow)

---

## Estructura del proyecto

```
PicSorter/
│
├── assets/
│   ├── modelo_fachadas.pt
│   ├── clases_fachadas.json
│   ├── categorias_fachadas.json
│   ├── modelo_cubiertas_plana.pt
│   ├── clases_cubiertas_plana.json
│   ├── categorias_cubiertas_plana.json
│   └── icono.ico
│
├── Main.py
├── gui.py
├── menu.py
├── classifier.py
├── downloader.py
├── organizer.py
├── report.py
│
└── README.md
```

---

## Instalación (modo desarrollo)

1. Clonar el repositorio:

```
git clone https://github.com/tuusuario/PicSorter.git
cd PicSorter
```

2. Crear entorno virtual:

```
python -m venv env
env\Scripts\activate
```

3. Instalar dependencias:

```
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```
python Main.py
```

---

## Uso de la aplicación

1. Seleccionar el tipo de proyecto:

   * Fachadas
   * Cubiertas (plana)

2. Ingresar el nombre del conjunto

3. Seleccionar:

   * Carpeta de origen (imágenes)
   * Carpeta de destino

4. Ejecutar el proceso

---

## Flujo de procesamiento

El sistema realiza las siguientes etapas:

1. Carga de imágenes desde la carpeta seleccionada
2. Extracción de características con CLIP
3. Clasificación mediante:

   * Modelo entrenado (si existe)
   * Clasificación por similitud de texto (fallback)
4. Organización de imágenes por actividad
5. Generación de reporte

---

## Estructura de salida

Ejemplo real de organización generada:

```
destino/
└── fachadas/
    └── conjunto_ejemplo/
        ├── anclajes/
        ├── acabados_muro/
        ├── sellado_ventanas/
        ├── ventanas/
        ├── instalaciones/
        ├── intervencion/
        ├── danos_inspeccion/
        ├── interior/
        ├── cubierta_visible/
        └── Revisar/
```

Para cubiertas:

```
destino/
└── cubiertas/
    └── conjunto_ejemplo/
        ├── anclajes/
        ├── seguridad/
        ├── arreglo_tejas/
        ├── levantamiento_manto/
        ├── alistamiento/
        ├── rependientado/
        ├── instalacion_manto/
        ├── carpinteria/
        ├── marquesinas/
        ├── tuberia_gas/
        └── Revisar/
```

Las imágenes con baja confianza (por debajo del umbral definido) se envían automáticamente a la carpeta `Revisar`.

---

## Reporte generado

El sistema crea un archivo:

```
reporte.txt
```

Ejemplo de contenido:

```
=== Reporte PicSorter ===

Resumen por conjunto y actividad:

Conjunto: conjunto_ejemplo
  - anclajes: 12 fotos
  - ventanas: 25 fotos
  - intervencion: 40 fotos
  - Revisar: 8 fotos

=== Detalle de fotos clasificadas ===

IMG_001.jpg -> conjunto_ejemplo / anclajes (92.34%)
IMG_002.jpg -> conjunto_ejemplo / ventanas (87.12%)
IMG_003.jpg -> conjunto_ejemplo / Revisar (65.20%)
```

---

## Modelo

El sistema utiliza:

* CLIP para extracción de características visuales
* Un clasificador entrenado sobre embeddings de imágenes

Si no existe un modelo entrenado, el sistema utiliza clasificación por similitud entre imagen y descripciones de categorías.

---

## Generación de ejecutable

Para crear el ejecutable:

```
pyinstaller PicSorter.spec
```

El ejecutable generado incluye:

* Modelos
* Archivos de configuración
* Recursos (iconos, categorías)

---

## Consideraciones

* La precisión depende directamente de la calidad y balance del dataset
* Clases visualmente similares pueden generar confusión
* Se recomienda agrupar categorías cuando exista alta ambigüedad visual
* Es importante mantener consistencia entre entrenamiento y uso real

---

## Estado del proyecto

* Clasificación funcional con precisión entre 80% y 90%
* Sistema estable en entorno de escritorio
* Preparado para uso operativo con validación manual (carpeta Revisar)

---

## Autor

Damian Rojas Castillo
