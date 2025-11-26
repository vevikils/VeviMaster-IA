import subprocess
import json
import re
import math
import logging

logger = logging.getLogger(__name__)

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
        # 1. LUFS and True Peak using ebur128
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
        output = result_lufs.stderr

        # Estrategia robusta: Buscar todas las ocurrencias de "I: ... LUFS"
        # El resumen final siempre está al final de la salida.
        # Las actualizaciones de progreso no suelen tener este formato exacto.
        matches = re.findall(r'I:\s+([-]?\d+(?:\.\d+)?)\s+LUFS', output)
        
        if matches:
            # Tomamos el último valor encontrado, que corresponde al Summary
            metrics['lufs'] = float(matches[-1])
            logger.info(f"LUFS detectado (findall last match): {metrics['lufs']}")
        else:
            logger.warning(f"WARNING: No se pudo detectar LUFS en {file_path}")
            logger.warning(f"Comando ejecutado: {' '.join(cmd_lufs)}")
            # Log full output only on failure
            logger.warning(f"Salida ffmpeg (últimos 1000 chars):\n{output[-1000:]}")
        # Debug: always log the output to see what ffmpeg is returning
        logger.info(f"Analizando LUFS para: {file_path}")
        
        if metrics['lufs'] == -70.0:
            logger.warning(f"WARNING: No se pudo detectar LUFS en {file_path}")
            logger.warning(f"Comando ejecutado: {' '.join(cmd_lufs)}")
            # Log full output only on failure
            logger.warning(f"Salida ffmpeg (últimos 1000 chars):\n{output[-1000:]}")

        # True Peak: take max of all channels
        peak_matches = re.findall(r'Peak:\s+([-]?\d+(?:\.\d+)?)\s+dBFS', output)
        if peak_matches:
            peaks = [float(p) for p in peak_matches]
            metrics['peak'] = max(peaks) if peaks else -70.0

        # 2. RMS using volumedetect
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

        # mean_volume (RMS)
        rms_match = re.search(r'mean_volume:\s+([-]?\d+(?:\.\d+)?)\s+dB', output_rms)
        if rms_match:
            metrics['rms'] = float(rms_match.group(1))

        # fallback for peak if not found earlier
        if metrics['peak'] == -70.0:
            peak_match = re.search(r'max_volume:\s+([-]?\d+(?:\.\d+)?)\s+dB', output_rms)
            if peak_match:
                metrics['peak'] = float(peak_match.group(1))

    except Exception as e:
        logger.error(f"Error analizando audio {file_path}: {e}", exc_info=True)

    return metrics
