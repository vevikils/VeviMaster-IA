import os
import shutil
import librosa
import soundfile as sf
import numpy as np

# Configuración sugerida
DATASET_SOURCE = "c:\\ruta\\a\\tus\\archivos_audio" # Cambia esto a tu carpeta de audios
DATASET_PROCESSED = "c:\\Users\\alfaswz\\Desktop\\vevi mastering ia django 31-7-25\\VeviMaster-IA\\dataset_ia_procesado"
GENRES = ["drill", "trap", "reggaeton", "hip_hop_clasico"]
CHUNK_LENGTH = 30 # segundos

def prepare_dataset(source_dir, output_dir, genres, chunk_sec=30):
    print(f"🚀 Iniciando preparación del dataset en: {output_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for genre in genres:
        genre_path = os.path.join(source_dir, genre)
        target_path = os.path.join(output_dir, genre)
        
        if not os.path.exists(genre_path):
            print(f"⚠️ Carpeta de género '{genre}' no encontrada. Creándola vacía...")
            os.makedirs(target_path, exist_ok=True)
            continue
            
        os.makedirs(target_path, exist_ok=True)
        files = [f for f in os.listdir(genre_path) if f.endswith(('.mp3', '.wav'))]
        
        print(f"📂 Procesando {len(files)} archivos de {genre}...")
        
        count = 0
        for i, file_name in enumerate(files):
            try:
                file_path = os.path.join(genre_path, file_name)
                # Cargar audio (remuestrear a 16kHz para el modelo AST de HuggingFace)
                y, sr = librosa.load(file_path, sr=16000)
                
                # Cortar en trozos de 30 segundos
                samples_per_chunk = chunk_sec * sr
                num_chunks = int(len(y) / samples_per_chunk)
                
                for j in range(num_chunks):
                    chunk = y[j * samples_per_chunk : (j + 1) * samples_per_chunk]
                    chunk_name = f"{genre}_{i}_{j}.wav"
                    chunk_path = os.path.join(target_path, chunk_name)
                    sf.write(chunk_path, chunk, sr)
                    count += 1
            except Exception as e:
                print(f"❌ Error al procesar {file_name}: {e}")
        
        print(f"✅ Se han generado {count} fragmentos para el género {genre}.")

if __name__ == "__main__":
    # Cambia la ruta origen a donde tengas tus audios
    if not os.path.exists(DATASET_SOURCE):
        print(f"🔴 ERROR: Cambia la variable DATASET_SOURCE en el script a la ruta donde guardas tus canciones.")
    else:
        prepare_dataset(DATASET_SOURCE, DATASET_PROCESSED, GENRES, CHUNK_LENGTH)
