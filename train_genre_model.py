import os
import torch
import numpy as np
import evaluate
import librosa
from datasets import Dataset, Features, Audio, ClassLabel
from transformers import (
    AutoModelForAudioClassification, 
    TrainingArguments, 
    Trainer
)

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset_ia_procesado")
MODEL_ID = "MIT/ast-finetuned-audioset-10-10-0.4593"
OUTPUT_DIR = os.path.join(BASE_DIR, "vevimaster_genre_model")

# Parámetros del modelo AST (Fijos)
TARGET_SR = 16000
MAX_LENGTH = 1024 # frames de tiempo
NUM_MEL_BINS = 128

def train_model():
    print("🚀 Escaneando carpetas de audio manualmente...")
    
    data = {"audio_path": [], "label": []}
    genres = [d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))]
    genres.sort()
    
    class_label = ClassLabel(names=genres)
    
    for genre in genres:
        genre_dir = os.path.join(DATASET_PATH, genre)
        for f in os.listdir(genre_dir):
            if f.endswith(".wav"):
                data["audio_path"].append(os.path.join(genre_dir, f))
                data["label"].append(class_label.str2int(genre))
    
    if not data["audio_path"]:
        print("🔴 No se encontraron archivos .wav.")
        return

    print(f"📊 Encontrados {len(data['audio_path'])} archivos en géneros: {genres}")
    
    raw_dataset = Dataset.from_dict(data)
    dataset_dict = raw_dataset.train_test_split(test_size=0.15, seed=42)

    # REEMPLAZO MANUAL DE FEATURE EXTRACTOR (Para evitar torchaudio)
    def manual_feature_extraction(audio_path):
        # Cargar audio
        y, _ = librosa.load(audio_path, sr=TARGET_SR, duration=10.0)
        # Calcular Mel Spectrogram (equivalente al que espera AST)
        S = librosa.feature.melspectrogram(y=y, sr=TARGET_SR, n_mels=NUM_MEL_BINS, fmin=0, fmax=8000, n_fft=400, hop_length=160)
        log_S = librosa.power_to_db(S, ref=np.max)
        
        # Normalizar y ajustar tamaño a [1024, 128]
        # AST espera (batch, time_frames, num_mel) -> (1024, 128)
        if log_S.shape[1] > MAX_LENGTH:
            log_S = log_S[:, :MAX_LENGTH]
        else:
            log_S = np.pad(log_S, ((0, 0), (0, MAX_LENGTH - log_S.shape[1])), mode='constant')
        
        # El modelo espera (1024, 128) pero librosa da (128, 1024), trasponemos:
        return log_S.T.astype(np.float32)

    def preprocess_function(examples):
        input_values = [manual_feature_extraction(path) for path in examples["audio_path"]]
        return {"input_values": input_values, "label": examples["label"]}

    print("🧠 Procesando dataset con Librosa (sin torchaudio)...")
    train_dataset = dataset_dict["train"].map(preprocess_function, batched=True, batch_size=4)
    eval_dataset = dataset_dict["test"].map(preprocess_function, batched=True, batch_size=4)

    # 3. Cargar el Modelo Base
    print(f"📥 Cargando modelo base: {MODEL_ID}")
    model = AutoModelForAudioClassification.from_pretrained(
        MODEL_ID,
        num_labels=len(genres),
        label2id={g: i for i, g in enumerate(genres)},
        id2label={i: g for i, g in enumerate(genres)},
        ignore_mismatched_sizes=True
    )

    # 4. Métricas
    accuracy = evaluate.load("accuracy")
    def compute_metrics(eval_pred):
        predictions = np.argmax(eval_pred.predictions, axis=1)
        return accuracy.compute(predictions=predictions, references=eval_pred.label_ids)

    # 5. Argumentos de entrenamiento
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=10, # Más épocas porque el dataset es pequeño
        logging_steps=5,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        fp16=torch.cuda.is_available(),
        remove_unused_columns=False, # Importante porque usamos input_values manuales
        report_to="none"
    )

    # 6. Iniciar Entrenamiento
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics,
    )

    print("🔥 ¡Entrenamiento en marcha! Cruzando los dedos...")
    trainer.train()

    # 7. Guardar el modelo final
    print(f"✅ ¡Éxito total! Guardado en {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)

if __name__ == "__main__":
    if not os.path.exists(DATASET_PATH):
        print(f"🔴 Error: No se encuentra la carpeta {DATASET_PATH}.")
    else:
        train_model()
