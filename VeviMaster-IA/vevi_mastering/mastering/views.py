import os
import uuid
import subprocess
import json
from django.conf import settings
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .utils import analyze_audio_metrics

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        if not audio_file.name.lower().endswith('.wav'):
            return HttpResponse('Solo se aceptan archivos WAV.', status=400)

        # Recoger parámetros del formulario (con valores por defecto si no vienen)
        def get_param(name, default, cast):
            val = request.POST.get(name)
            try:
                return cast(val) if val is not None else default
            except Exception:
                return default
        global_params = {
            'loudness': get_param('loudness', -8, float),
            'loudness_range': get_param('loudness_range', 6, float),
            'peak': get_param('peak', 0.98, float),
            'rms': get_param('rms', -10, float),
            'dynamics': get_param('dynamics', 2.5, float),
            'sharpness': get_param('sharpness', 2.2, float),
            'space': get_param('space', -3, float),
            'drr': get_param('drr', 12, float),
            'sample_rate': get_param('sample_rate', 44100, int),
            'channels': get_param('channels', 2, int),
        }

        # Recoger parámetros de las bandas (4 bandas)
        bands = []
        for i in range(4):
            band = {
                'low_freq': get_param(f'band_{i}_low_freq', 20, float),
                'high_freq': get_param(f'band_{i}_high_freq', 20000, float),
                'loudness': get_param(f'band_{i}_loudness', -18, float),
                'loudness_range': get_param(f'band_{i}_loudness_range', 6, float),
                'mid_mean': get_param(f'band_{i}_mid_mean', -15, float),
                'mid_to_side_loudness': get_param(f'band_{i}_mid_to_side_loudness', -10, float),
                'mid_to_side_loudness_range': get_param(f'band_{i}_mid_to_side_loudness_range', 10, float),
                'side_mean': get_param(f'band_{i}_side_mean', -20, float),
            }
            bands.append(band)

        # Crear JSON temporal de configuración
        config = {
            **global_params,
            'bands': bands
        }
        config_path = os.path.join(settings.MEDIA_ROOT, f'{uuid.uuid4()}_mastering_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        # Guardar archivo temporal
        input_filename = f'{uuid.uuid4()}_{audio_file.name}'
        input_path = os.path.join(settings.MEDIA_ROOT, input_filename)
        with open(input_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # ANALIZAR INPUT (ANTES)
        metrics_before = analyze_audio_metrics(input_path)

        # Nombre de salida
        base_name = os.path.splitext(audio_file.name)[0]
        output_filename = f'{base_name}_vevi_master_ia.wav'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # --- EJECUCIÓN CON PHASELIMITER (EXCLUSIVO DOCKER/LINUX) ---
        BASE_DIR = settings.BASE_DIR
        bin_dir = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'phaselimiter', 'bin')
        exe_name = 'phase_limiter'
        exe_path = os.path.join(bin_dir, exe_name)

        print(f"Usando motor: PhaseLimiter en {exe_path}")
        
        # Asegurar permisos (solo si estamos en Linux/Mac, aunque en Docker ya debería estar)
        if os.name != 'nt':
            try:
                import stat
                st = os.stat(exe_path)
                os.chmod(exe_path, st.st_mode | stat.S_IEXEC)
            except Exception:
                pass

        env = os.environ.copy()
        env['PATH'] = bin_dir + os.pathsep + env['PATH']
        
        cmd = [
            exe_path,
            f'-input={input_path}',
            f'-output={output_path}',
            f'-mastering_reference_file={config_path}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=BASE_DIR, env=env)
            if result.returncode != 0:
                return HttpResponse(f'Error en PhaseLimiter:<br><pre>{result.stderr}</pre>', status=500)
        except Exception as e:
            return HttpResponse(f'Error ejecutando PhaseLimiter: {e}', status=500)

        # ANALIZAR OUTPUT (DESPUÉS)
        metrics_after = analyze_audio_metrics(output_path)

        # Renderizar página de resultados
        context = {
            'metrics_before': metrics_before,
            'metrics_after': metrics_after,
            'output_filename': output_filename,
            'original_filename': audio_file.name,
            'engine_used': 'PhaseLimiter' if use_phaselimiter else 'FFmpeg (Modo Compatibilidad Windows)'
        }
        return render(request, 'mastering/results.html', context)

    return render(request, 'mastering/upload.html')

def download_master(request, filename):
    """
    Vista para descargar el archivo masterizado.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("El archivo no existe.")
