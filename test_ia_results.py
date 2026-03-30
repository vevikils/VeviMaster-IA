import os
import torch
import librosa
import numpy as np
import sys
from transformers import ASTForAudioClassification

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "vevimaster_genre_model")
TARGET_SR = 16000
MAX_LENGTH = 1024
NUM_MEL_BINS = 128

def extract_features(audio_path):
    print(f"🧠 Analizando audio: {os.path.basename(audio_path)}...")
    y, _ = librosa.load(audio_path, sr=TARGET_SR, duration=10.0)
    S = librosa.feature.melspectrogram(y=y, sr=TARGET_SR, n_mels=NUM_MEL_BINS, fmin=0, fmax=8000, n_fft=400, hop_length=160)
    log_S = librosa.power_to_db(S, ref=np.max)
    
    if log_S.shape[1] > MAX_LENGTH:
        log_S = log_S[:, :MAX_LENGTH]
    else:
        log_S = np.pad(log_S, ((0, 0), (0, MAX_LENGTH - log_S.shape[1])), mode='constant')
    
    return torch.tensor(log_S.T).unsqueeze(0).float()

def test_inference(audio_path):
    if not os.path.exists(MODEL_PATH):
        print(f"🔴 Error: No se encuentra el modelo en {MODEL_PATH}")
        return

    print(f"📥 Cargando modelo AST desde {MODEL_PATH}...")
    model = ASTForAudioClassification.from_pretrained(MODEL_PATH)
    model.eval()
    
    inputs = extract_features(audio_path)
    
    with torch.no_grad():
        logits = model(inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1)
    
    id2label = model.config.id2label
    print("\n📊 --- RESULTADOS DE TU NUEVA IA --- 📊")
    for i in range(len(id2label)):
        # Convertir i a el tipo que tenga la clave (int o str)
        label = id2label.get(i) or id2label.get(str(i)) or f"Clase {i}"
        conf = float(probs[0][i]) * 100
        bar = "█" * int(conf / 5)
        print(f"{label.upper():<12} | {conf:>6.2f}% | {bar}")
    print("--------------------------------------\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso: python test_ia_results.py ruta/a/tu_cancion.wav")
    else:
        test_inference(sys.argv[1])
