import subprocess
import json
import re
import math
import logging

logger = logging.getLogger(__name__)

def analyze_audio_metrics(file_path):
    """
    Analiza un archivo de audio usando ffmpeg para obtener LUFS, True Peak y RMS
    en un solo paso para máxima velocidad.
    """
    metrics = {
        'lufs': -70.0,
        'peak': -70.0,
        'rms': -70.0
    }

    try:
        # Combinamos ebur128 y volumedetect. ebur128=peak=true da el True Peak.
        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-af', 'ebur128=peak=true,volumedetect',
            '-f', 'null',
            '-'
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        output = result.stderr

        # 1. Parse LUFS (Integrated Summary - tomamos el último valor del log que es el resumen final)
        lufs_vals = re.findall(r'I:\s+([-]?\d+(?:\.\d+)?)\s+LUFS', output, re.IGNORECASE)
        if lufs_vals:
            metrics['lufs'] = float(lufs_vals[-1])

        # 2. Parse LRA (Loudness Range Summary)
        lra_vals = re.findall(r'LRA:\s+([-]?\d+(?:\.\d+)?)\s+LU', output, re.IGNORECASE)
        if lra_vals:
            metrics['lra'] = float(lra_vals[-1])
        else:
            metrics['lra'] = 10.0

        # 3. Parse Threshold
        thresh_vals = re.findall(r'Threshold:\s+([-]?\d+(?:\.\d+)?)\s+LUFS', output, re.IGNORECASE)
        if thresh_vals:
            metrics['threshold'] = float(thresh_vals[-1])
        else:
            metrics['threshold'] = -25.0

        # 4. Parse True Peak (Summary)
        peak_vals = re.findall(r'(?:True peak|Peak):\s+([-]?\d+(?:\.\d+)?)\s+dBFS', output, re.IGNORECASE)
        if not peak_vals:
             peak_vals = re.findall(r'max_volume:\s+([-]?\d+(?:\.\d+)?)\s+dB', output, re.IGNORECASE)
        
        if peak_vals:
            metrics['peak'] = float(peak_vals[-1])

        # 5. Parse RMS (Mean Volume - tomamos el último resumen)
        rms_vals = re.findall(r'mean_volume:\s+([-]?\d+(?:\.\d+)?)\s+dB', output, re.IGNORECASE)
        if rms_vals:
            metrics['rms'] = float(rms_vals[-1])
        else:
            # Estimación profesional basada en LUFS
            metrics['rms'] = metrics['lufs'] - 1.2

        logger.info(f"Métricas Finales: {metrics}")

    except Exception as e:
        logger.error(f"Error crítico en analyze_audio_metrics: {e}")

    return metrics

def analyze_spectrum(file_path, n_fft=2048, duration=30):
    """
    Calcula el espectro de frecuencia promedio de un archivo de audio.
    Retorna dos listas: freqs (eje X) y magnitudes_db (eje Y).
    """
    import librosa
    import numpy as np

    try:
        # Cargar audio (limitado a 'duration' segundos del centro para rapidez)
        # Obtenemos primero la duración total
        full_duration = librosa.get_duration(filename=file_path)
        offset = max(0, (full_duration - duration) / 2)
        
        # Cargar audio SIEMPRE a la misma frecuencia para que la comparación sea justa
        # sr=22050 es suficiente para análisis espectral visual y es mucho más rápido
        y, sr_fixed = librosa.load(file_path, sr=22050, offset=offset, duration=duration)
        
        # Calcular STFT
        S = np.abs(librosa.stft(y, n_fft=n_fft))
        
        # Promediar en el tiempo para obtener un solo espectro
        S_mean = np.mean(S, axis=1)
        
        # Convertir a dB usando una referencia fija absoluta para que se vea la diferencia de volumen
        db_values = librosa.amplitude_to_db(S_mean, ref=1.0)
        
        # Generar eje de frecuencias basado en la nueva SR fija
        freqs = librosa.fft_frequencies(sr=sr_fixed, n_fft=n_fft)
        
        # Filtrar y suavizar para el gráfico (reducir puntos)
        # Tomamos 100 puntos distribuidos logarítmicamente para cubrir 20Hz - 20kHz
        target_freqs = np.logspace(np.log10(20), np.log10(20000), num=100)
        
        # Interpolación simple para obtener los valores en esas frecuencias target
        # db_values y freqs tienen el mismo tamaño (n_fft/2 + 1)
        # Usamos np.interp
        interpolated_db = np.interp(target_freqs, freqs, db_values)
        
        logger.info(f"Espectro calculado para {file_path}. Primeros valores: {interpolated_db[:3]}")
        
        return {
            'labels': [int(f) for f in target_freqs],
            'data': [float(v) for v in interpolated_db]
        }
        
    except Exception as e:
        logger.error(f"Error calculando espectro para {file_path}: {e}")
        return {'labels': [], 'data': []}
def convert_to_wav(input_path, output_path):
    """
    Convierte cualquier archivo de audio (MP3, etc) a WAV 44.1kHz 16-bit stereo.
    """
    cmd = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-ar', '44100',
        '-ac', '2',
        '-sample_fmt', 's16',
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
