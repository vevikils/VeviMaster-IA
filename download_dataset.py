import os
import subprocess
import re
import sys

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MARKDOWN_FILE = os.path.join(BASE_DIR, "DATASET_CURACION_URBANO.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset_ia_procesado")
GENRES = ["drill", "trap", "reggaetón"]

def clean_filename(name):
    """Limpia el nombre para evitar caracteres raros en Windows."""
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_").lower()

def parse_markdown(file_path):
    print(f"📖 Leyendo lista de canciones desde {file_path}...")
    songs = []
    
    if not os.path.exists(file_path):
        print(f"🔴 Error: No se encuentra el archivo {file_path}")
        return songs

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Dividir contenido por géneros para asignar la carpeta correcta
    sections = re.split(r"## (?:🎧 SECCIÓN 1: |🔥 SECCIÓN 2: |🌴 SECCIÓN 3: )", content)
    
    if len(sections) < 4:
        print("⚠️ No se han detectado las 3 secciones de género correctamente.")
        return []

    for i, section in enumerate(sections[1:]):
        genre = GENRES[i]
        # Captura filas: | Artista | Título | Año | ... |
        matches = re.findall(r"\|\s*(?!Artista|--)([^|]+)\s*\|\s*([^|]+)\s*\|\s*\d{4}\s*\|", section)
        for artista, titulo in matches:
            artista = artista.strip()
            titulo = titulo.strip()
            if artista == "..." or titulo == "...": continue
            
            songs.append({
                "artista": artista,
                "titulo": titulo,
                "query": f"{artista} {titulo}",
                "genre": genre,
                "filename": clean_filename(f"{artista}_{titulo}.wav")
            })
            
    return songs

def download_audio(song_data, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    final_path = os.path.join(output_folder, song_data["filename"])
    
    # COMPROBAR SI YA EXISTE PARA SALTARLO 💨
    if os.path.exists(final_path):
        print(f"⏩ Saltando (ya existe): {song_data['artista']} - {song_data['titulo']}")
        return

    print(f"🎵 Descargando: {song_data['artista']} - {song_data['titulo']}...")
    
    # Comando yt-dlp: máximo audio, formato wav, 16kHz, mono
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--quiet",
        "--no-playlist",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--output", f"{output_folder}/%(title)s.%(ext)s", # bajada temporal
        "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1",
        f"ytsearch1:{song_data['query']}"
    ]
    
    try:
        # Descargar a un temporal y luego renombrar para tener control total
        subprocess.run(cmd, check=True)
        # Buscar el archivo .wav que se acaba de crear (yt-dlp usa el título de youtube)
        # Como no sabemos el título exacto de youtube, buscamos el .wav más reciente en la carpeta
        files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith(".wav")]
        if files:
            latest_file = max(files, key=os.path.getctime)
            # Si no es ya el nombre que queremos, lo renombramos
            if os.path.basename(latest_file) != song_data["filename"]:
                os.replace(latest_file, final_path)
        print(f"✅ Éxito.")
    except Exception as e:
        print(f"❌ Error al descargar {song_data['query']}: {e}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    songs = parse_markdown(MARKDOWN_FILE)
    
    if not songs:
        print("🔴 No se han encontrado canciones para descargar.")
        return

    print(f"🚀 Iniciando procesamiento de {len(songs)} temas...")
    
    for song in songs:
        genre_folder = os.path.join(OUTPUT_DIR, song["genre"])
        download_audio(song, genre_folder)

    print("🏁 ¡Proceso completado! Tu dataset de 150+ canciones está listo para la IA.")

if __name__ == "__main__":
    main()
