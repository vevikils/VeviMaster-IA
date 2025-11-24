import subprocess
import json
import re
import math

def analyze_audio_metrics(file_path):
    """
    Analiza un archivo de audio usando ffmpeg para obtener LUFS, True Peak y RMS.
    Retorna un diccionario con las métricas.
    """
    metrics = {
        'lufs': -70.0,  # Valor por defecto (silencio)
        'peak': -70.0,
        'rms': -70.0
    }

    try:
        # Comando para obtener LUFS (Integrated Loudness) y True Peak usando el filtro ebur128
        # y volumedetect para RMS (aunque ebur128 es más completo para loudness)
        
        # 1. Análisis de Loudness (LUFS y True Peak) con ebur128
        cmd_lufs = [
            'ffmpeg',
            '-i', file_path,
            '-filter_complex', 'ebur128=peak=true',
            '-f', 'null',
            '-'
        ]
        
        result_lufs = subprocess.run(
            cmd_lufs, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace'
        )
        
        # Parsear salida de ebur128
        output = result_lufs.stderr
        
        # Buscar Integrated loudness
        lufs_match = re.search(r'I:\s+([-\d\.]+)\s+LUFS', output)
        if lufs_match:
            metrics['lufs'] = float(lufs_match.group(1))
            
        # Buscar True Peak (tomamos el máximo de todos los canales)
        peak_matches = re.findall(r'Peak:\s+([-\d\.]+)\s+dBFS', output)
        if peak_matches:
            # Convertir a float y tomar el máximo
            peaks = [float(p) for p in peak_matches]
            metrics['peak'] = max(peaks) if peaks else -70.0

        # 2. Análisis de RMS con volumedetect (es rápido y estándar)
        cmd_rms = [
            'ffmpeg',
            '-i', file_path,
            '-filter:a', 'volumedetect',
            '-f', 'null',
            '-'
        ]
        
        result_rms = subprocess.run(
            cmd_rms, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace'
        )
        
        output_rms = result_rms.stderr
        
        # Buscar mean_volume (RMS)
        rms_match = re.search(r'mean_volume:\s+([-\d\.]+)\s+dB', output_rms)
        if rms_match:
            metrics['rms'] = float(rms_match.group(1))
            
        # Si no encontramos Peak con ebur128, intentamos con volumedetect (max_volume)
        if metrics['peak'] == -70.0:
            peak_match = re.search(r'max_volume:\s+([-\d\.]+)\s+dB', output_rms)
            if peak_match:
                metrics['peak'] = float(peak_match.group(1))

    except Exception as e:
        print(f"Error analizando audio {file_path}: {e}")
        
    return metrics
