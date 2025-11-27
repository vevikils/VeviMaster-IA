import os
import shutil
import uuid
import subprocess
import json
import logging
from django.conf import settings
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .utils import analyze_audio_metrics

logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def upload_audio(request):
    """Handle audio upload, run PhaseLimiter and return metrics before/after."""
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        if not audio_file.name.lower().endswith('.wav'):
            return HttpResponse('Solo se aceptan archivos WAV.', status=400)

        # Helper to get parameters with defaults
        def get_param(name, default, cast):
            val = request.POST.get(name)
            try:
                return cast(val) if val is not None else default
            except Exception:
                return default

        # Global mastering parameters – PhaseLimiter uses 'reference' (target LUFS) and 'reference_mode'
        global_params = {
            'reference': get_param('loudness', -8, float),   # target integrated LUFS
            'reference_mode': 'loudness',
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

        # Band parameters (4 bands)
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

        # Build configuration JSON (PhaseLimiter expects specific keys)
        config = {
            **global_params,
            'bands': bands,
            # PhaseLimiter specific flag – will be filled with the path below
            'mastering5_mastering_reference_file': None,
            'mastering5_mastering_level': 0.5,
            'mastering5_optimization_algorithm': 'de_prmm',
            'mastering5_optimization_max_eval_count': 40000,
        }
        # Save JSON and set the reference file path
        config_path = os.path.join(settings.MEDIA_ROOT, f'{uuid.uuid4()}_mastering_config.json')
        config['mastering5_mastering_reference_file'] = config_path
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Mastering configuration saved to {config_path}")

        # Save uploaded file temporarily
        input_filename = f'{uuid.uuid4()}_{audio_file.name}'
        input_path = os.path.join(settings.MEDIA_ROOT, input_filename)
        with open(input_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # Analyze before mastering
        metrics_before = analyze_audio_metrics(input_path)

        # Prepare PhaseLimiter execution
        base_name = os.path.splitext(audio_file.name)[0]
        output_filename = f'{base_name}_vevi_master_ia.wav'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        BASE_DIR = settings.BASE_DIR
        bin_dir = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'phaselimiter', 'bin')
        exe_path = os.path.join(bin_dir, 'phase_limiter')

        # Ensure executable permission on Linux
        if os.name != 'nt':
            try:
                import stat
                st = os.stat(exe_path)
                os.chmod(exe_path, st.st_mode | stat.S_IEXEC)
            except Exception:
                pass

        env = os.environ.copy()
        env['PATH'] = bin_dir + os.pathsep + env['PATH']
        temp_output_path = os.path.join('/tmp', f'temp_{uuid.uuid4()}.wav')
        cmd = [
            exe_path,
            f'-input={input_path}',
            f'-output={temp_output_path}',
            f'-mastering5_mastering_reference_file={config_path}',
            f'-reference={global_params["reference"]}',
            f'-reference_mode={global_params["reference_mode"]}',
            f'-mastering5_mastering_level=3.5',
        ]
        # Run PhaseLimiter with detailed logging
        logger.info(f"Executing PhaseLimiter command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=BASE_DIR, env=env)
        logger.info(f"PhaseLimiter STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"PhaseLimiter STDERR:\n{result.stderr}")
        if result.returncode != 0:
            return HttpResponse(f'Error en PhaseLimiter:<br><pre>{result.stderr}</pre>', status=500)
        if os.path.exists(temp_output_path):
            shutil.move(temp_output_path, output_path)
        else:
            return HttpResponse('Error: PhaseLimiter no generó el archivo de salida esperado.', status=500)

        # Analyze after mastering
        metrics_after = analyze_audio_metrics(output_path)

        context = {
            'metrics_before': metrics_before,
            'metrics_after': metrics_after,
            'output_filename': output_filename,
            'original_filename': audio_file.name,
            'engine_used': 'PhaseLimiter',
        }
        return render(request, 'mastering/results.html', context)
    # GET request – render upload form
    return render(request, 'mastering/upload.html')

@login_required
def download_master(request, filename):
    """Vista para descargar el archivo masterizado."""
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("El archivo no existe.")
