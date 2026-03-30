# Plan de Entrenamiento: IA personalizada (AST) para Géneros Modernos

Este documento detalla la hoja de ruta para entrenar tu propia Inteligencia Artificial basada en el **Audio Spectrogram Transformer (AST)** de Hugging Face. A diferencia de `musicnn`, este modelo tratará los audios como imágenes de sonido (espectrogramas), lo que permite una precisión mucho mayor en subgéneros rítmicos.

---

## 📂 1. Preparación del Dataset (MANDATORIO)
Para que la IA aprenda, necesitamos que organices una carpeta de entrenamiento. La IA no sabe qué es el Drill o el Trap hasta que vea suficientes ejemplos.

**Estructura requerida:**
Crea una carpeta llamada `dataset_entrenamiento` con subcarpetas por género:
- `dataset_entrenamiento/drill/` -> Mete aquí todos los archivos de Drill que tengas (.wav o .mp3).
- `dataset_entrenamiento/trap/` -> Todos tus archivos de Trap.
- `dataset_entrenamiento/reggaeton/` -> Todos tus archivos de Reggaeton.
- `dataset_entrenamiento/hip_hop_clasico/` -> Rap normal para que la IA sepa distinguirlos.

> [!TIP]
> **Cantidad mínima:** 50 canciones por carpeta.
> **Cantidad ideal:** 200 canciones por carpeta.
> **Duración:** No importa si son canciones enteras, el script recortará 30 segundos de cada una automáticamente.

---

## 🛠️ 2. Instalación de Herramientas de "Deep Learning"
Necesitaremos instalar las librerías de IA más modernas en tu servidor o PC de entrenamiento:

```powershell
pip install transformers datasets torch torchaudio accelerate evaluate
```

---

## 🧠 3. Script de Entrenamiento (Lo crearé yo)
Una vez tengas las carpetas listas, ejecutaré un script de Python que:
1.  **Cargará el modelo base:** `MIT/ast-finetuned-audioset`.
2.  **Ajustará el "Cerebro":** Reemplazará la última capa para que solo clasifique tus géneros.
3.  **Entrenará:** Procesará todos tus audios (esto requiere mucha potencia de CPU o GPU).
4.  **Guardará el modelo:** Generará una carpeta llamada `vevimaster_genre_model/`.

---

## 🔌 4. Integración Final en Django
Cuando el entrenamiento termine, modificaré `analyzer/views.py` para que:
1.  En lugar de importar `musicnn`, importe tu nuevo modelo local.
2.  El análisis detecte instantáneamente si un beat es Drill con precisión milimétrica.

---

## 🚀 ¿Cómo empezamos?
1.  **Confírmame:** ¿Tienes ya una colección de canciones de estos géneros en tu PC o servidor?
2.  Si la respuesta es sí, **dime la ruta de la carpeta** donde están los audios y procederé a crearte el script de preparación para empezar el entrenamiento ahora mismo.
