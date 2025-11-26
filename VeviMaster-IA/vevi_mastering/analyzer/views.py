from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
from typing import Dict, List, Tuple

from .forms import AudioUploadForm
from .models import AudioAnalysis

# Importar funciones de análisis (opcional)
try:
    from musicnn.tagger import top_tags
    MUSICNN_AVAILABLE = True
except ImportError:
    MUSICNN_AVAILABLE = False
    top_tags = None

# Importar desde el módulo genres_moods en el directorio raíz del proyecto
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

try:
    from genres_moods import (
        TARGET_GENRES,
        MOOD_CATEGORIES,
        map_genre_tag_to_target,
        map_tag_to_mood,
    )
    GENRES_MOODS_AVAILABLE = True
except ImportError:
    GENRES_MOODS_AVAILABLE = False
    TARGET_GENRES = []
    MOOD_CATEGORIES = []
    map_genre_tag_to_target = lambda x: None
    map_tag_to_mood = lambda x: None


def aggregate_genre_percentages(tags: List[str], scores: List[float]) -> Dict[str, float]:
    """Agrega porcentajes de géneros"""
    raw_scores: Dict[str, float] = {g: 0.0 for g in TARGET_GENRES}
    for tag, score in zip(tags, scores):
        mapped = map_genre_tag_to_target(tag)
        if mapped is not None:
            raw_scores[mapped] += float(score)

    total = sum(raw_scores.values())
    if total <= 0:
        return {g: 0.0 for g in TARGET_GENRES}
    # Normalizar a porcentajes que sumen 100
    return {g: (v / total) * 100.0 for g, v in raw_scores.items()}


def infer_mood(tags: List[str], scores: List[float]) -> Tuple[str, float, Dict[str, float]]:
    """Infiere el estado de ánimo"""
    mood_scores: Dict[str, float] = {m: 0.0 for m in MOOD_CATEGORIES}
    for tag, score in zip(tags, scores):
        mood = map_tag_to_mood(tag)
        if mood is not None:
            mood_scores[mood] += float(score)

    # Elegir el mood con mayor puntuación
    best_mood = max(mood_scores.items(), key=lambda kv: kv[1])
    total = sum(mood_scores.values())
    confidence = 0.0 if total <= 0 else (best_mood[1] / total) * 100.0
    return best_mood[0], confidence, mood_scores


def analyze_audio(audio_path: str, top_n: int = 50) -> Dict:
    """Analiza un archivo de audio y retorna los resultados"""
    if not MUSICNN_AVAILABLE:
        return {
            'success': False,
            'error': 'musicnn no está instalado. Instala las dependencias de análisis de música.'
        }
    
    try:
        # Obtener tags del modelo
        # Desactivar print_tags para evitar output en el servidor
        result = top_tags(audio_path, model="MSD_musicnn", topN=top_n, print_tags=False)
        
        # top_tags puede devolver diferentes formatos dependiendo de la versión
        # Manejar todos los casos posibles de forma segura
        if isinstance(result, tuple):
            # Si es una tupla, extraer los valores
            if len(result) == 2:
                tags, scores = result
            elif len(result) > 2:
                # Si tiene más de 2 valores, tomar solo los primeros dos
                tags = result[0]
                scores = result[1]
            else:
                # Si solo tiene un valor, asumir que son tags
                tags = result[0] if len(result) == 1 else []
                scores = [1.0] * len(tags) if isinstance(tags, list) else [1.0]
        elif isinstance(result, list):
            # Si es una lista
            # Verificar si es una lista de strings (solo tags)
            if len(result) > 0 and isinstance(result[0], str):
                tags = result
                # Generar scores basados en el ranking (decay lineal)
                # El primero tiene 1.0, el último tiene cerca de 0
                # Esto es crucial porque si topN es alto (ej. 50), musicnn devuelve
                # casi todo el vocabulario, y si damos 1.0 a todo, el resultado es siempre igual.
                count = len(tags)
                scores = [float(count - i) / count for i in range(count)]
            elif len(result) >= 2:
                tags = result[0]
                scores = result[1]
            elif len(result) == 1:
                # Si solo hay un elemento, verificar si es una lista anidada
                if isinstance(result[0], (tuple, list)) and len(result[0]) >= 2:
                    tags = result[0][0]
                    scores = result[0][1]
                else:
                    tags = result[0]
                    scores = [1.0] * len(tags) if isinstance(tags, list) else [1.0]
            else:
                tags = []
                scores = []
        else:
            # Si no es tupla ni lista, asumir que es solo tags
            tags = [result] if not isinstance(result, list) else result
            scores = [1.0] * len(tags) if isinstance(tags, list) else [1.0]
        
        # Asegurar que tags y scores son listas
        if not isinstance(tags, list):
            tags = list(tags) if tags else []
        if not isinstance(scores, list):
            scores = list(scores) if scores else []
        
        # Verificar que tienen la misma longitud
        if len(tags) != len(scores):
            # Si no coinciden, ajustar scores
            if len(scores) < len(tags):
                # Rellenar con 1.0 si faltan scores
                scores.extend([1.0] * (len(tags) - len(scores)))
            else:
                # Cortar scores si sobran
                scores = scores[:len(tags)]
        
        # Convertir scores a lista de floats
        scores = [float(s) for s in scores]
        
        # Agregar géneros
        genres_pct = aggregate_genre_percentages(tags, scores)
        
        # Inferir mood
        mood, mood_conf, mood_scores = infer_mood(tags, scores)
        
        return {
            'success': True,
            'genres_percent': genres_pct,
            'mood': mood,
            'mood_confidence': mood_conf,
            'raw_tags': tags,
            'raw_scores': scores,
            'mood_scores': mood_scores,
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def index(request):
    """Vista principal para subir y analizar audio"""
    if request.method == 'POST':
        # Prevenir doble envío usando sesión
        if 'processing_file' in request.session:
            # Si ya hay un archivo en procesamiento, rechazar el nuevo envío
            messages.warning(request, 'Ya hay un archivo en procesamiento. Por favor espera.')
            form = AudioUploadForm()
        else:
            form = AudioUploadForm(request.POST, request.FILES)
            
            # Verificar que hay un archivo en request.FILES antes de validar
            if 'audio_file' not in request.FILES or not request.FILES['audio_file']:
                messages.error(request, 'Por favor, selecciona un archivo de audio.')
                form = AudioUploadForm()
            else:
                if form.is_valid():
                    audio_file = form.cleaned_data['audio_file']
                    
                    # Verificar que realmente hay un archivo
                    if not audio_file or not audio_file.name:
                        messages.error(request, 'Por favor, selecciona un archivo de audio válido.')
                        form = AudioUploadForm()
                    else:
                        try:
                            # Marcar que estamos procesando un archivo
                            request.session['processing_file'] = True
                            request.session.modified = True
                            
                            # Guardar el archivo
                            analysis = AudioAnalysis(audio_file=audio_file)
                            analysis.save()
                            
                            # Obtener la ruta del archivo guardado
                            audio_path = analysis.audio_file.path
                            
                            # Verificar que el archivo existe
                            if not os.path.exists(audio_path):
                                messages.error(request, 'Error: El archivo no se guardó correctamente.')
                                if analysis.id:
                                    analysis.delete()
                                form = AudioUploadForm()
                            else:
                                # Analizar el audio
                                result = analyze_audio(audio_path)
                                
                                if result['success']:
                                    # Guardar resultados en el modelo
                                    analysis.genres_percent = result['genres_percent']
                                    analysis.mood = result['mood']
                                    analysis.mood_confidence = result['mood_confidence']
                                    analysis.raw_tags = result['raw_tags']
                                    analysis.raw_scores = result['raw_scores']
                                    analysis.mood_scores = result['mood_scores']
                                    analysis.save()
                                    
                                    # Limpiar la bandera de procesamiento
                                    if 'processing_file' in request.session:
                                        del request.session['processing_file']
                                    
                                    messages.success(request, '¡Análisis completado exitosamente!')
                                    return redirect('analyzer:results', analysis_id=analysis.id)
                                else:
                                    error_msg = result.get("error", "Error desconocido")
                                    messages.error(request, f'Error al analizar el audio: {error_msg}')
                                    # Eliminar el análisis fallido
                                    if analysis.id:
                                        try:
                                            # Intentar eliminar el archivo físico
                                            if os.path.exists(audio_path):
                                                os.remove(audio_path)
                                        except:
                                            pass
                                        analysis.delete()
                            
                            # Limpiar la bandera de procesamiento en caso de error
                            if 'processing_file' in request.session:
                                del request.session['processing_file']
                                request.session.modified = True
                                
                        except Exception as e:
                            # Limpiar la bandera de procesamiento
                            if 'processing_file' in request.session:
                                del request.session['processing_file']
                                request.session.modified = True
                            messages.error(request, f'Error al procesar el archivo: {str(e)}')
                            form = AudioUploadForm()
                else:
                    # Si el formulario no es válido, mostrar errores
                    if not form.errors:
                        messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        # Limpiar la bandera de procesamiento si se accede por GET
        if 'processing_file' in request.session:
            del request.session['processing_file']
            request.session.modified = True
        form = AudioUploadForm()
    
    # Obtener análisis recientes
    recent_analyses = AudioAnalysis.objects.all()[:10]
    
    return render(request, 'analyzer/index.html', {
        'form': form,
        'recent_analyses': recent_analyses,
    })


def results(request, analysis_id):
    """Vista para mostrar los resultados del análisis"""
    try:
        analysis = AudioAnalysis.objects.get(id=analysis_id)
    except AudioAnalysis.DoesNotExist:
        messages.error(request, 'Análisis no encontrado.')
        return redirect('analyzer:index')
    
    top_genres = analysis.get_top_genres(top_n=10)
    
    # Format mood_confidence for display
    mood_confidence_display = f"{analysis.mood_confidence:.1f}" if analysis.mood_confidence else "0.0"
    
    return render(request, 'analyzer/results.html', {
        'analysis': analysis,
        'top_genres': top_genres,
        'mood_confidence_display': mood_confidence_display,
    })


def api_results(request, analysis_id):
    """API endpoint para obtener resultados en JSON"""
    try:
        analysis = AudioAnalysis.objects.get(id=analysis_id)
        return JsonResponse({
            'success': True,
            'audio': analysis.audio_file.url,
            'genres_percent': analysis.genres_percent,
            'mood': analysis.mood,
            'mood_confidence': analysis.mood_confidence,
            'raw': {
                'tags': analysis.raw_tags,
                'scores': analysis.raw_scores,
                'mood_scores': analysis.mood_scores,
            },
        })
    except AudioAnalysis.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Análisis no encontrado'
        }, status=404)
