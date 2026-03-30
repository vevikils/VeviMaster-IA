from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
import json
import sys
import warnings
import logging
from typing import Dict, List, Tuple

# IMPORTACIONES CRÍTICAS
from .forms import AudioUploadForm
from .models import AudioAnalysis

logger = logging.getLogger(__name__)

# CONFIGURACIÓN DE RUTAS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AST_LOAD_ERROR = "Iniciando..."
AST_MODEL_INSTANCE = None

def get_ast_model():
    global AST_MODEL_INSTANCE, AST_LOAD_ERROR
    if AST_MODEL_INSTANCE is None:
        selected_path = os.path.join(BASE_DIR, "vevimaster_genre_model")
        if not os.path.exists(selected_path):
             AST_LOAD_ERROR = f"Carpeta no encontrada en {selected_path}"
             return None
        try:
            from transformers import ASTForAudioClassification
            AST_MODEL_INSTANCE = ASTForAudioClassification.from_pretrained(selected_path)
            AST_MODEL_INSTANCE.eval()
            AST_LOAD_ERROR = "¡Dataset Cargado con éxito!"
        except Exception as e:
            AST_LOAD_ERROR = f"Error al despertar la IA: {e}"
    return AST_MODEL_INSTANCE

def aggregate_genre_percentages(tags, scores):
    # Diccionario base con todos los géneros que queremos mostrar
    URBAN_KEYS = ['drill', 'trap', 'reggaeton', 'hyperpop']
    ALL_KEYS = URBAN_KEYS + ['pop', 'rock', 'hip hop', 'electronic', 'jazz', 'classical', 'metal', 'blues', 'country', 'reggae', 'folk', 'r&b', 'soul', 'funk', 'house', 'techno', 'ambient', 'latin', 'punk', 'disco']
    
    raw_scores = {g: 0.0 for g in ALL_KEYS}
    
    for tag, score in zip(tags, scores):
        tag_l = str(tag).lower().strip()
        mapped = tag_l
        try:
            from genres_moods import map_genre_tag_to_target
            m = map_genre_tag_to_target(tag_l)
            if m: mapped = m
        except Exception: pass
        
        if mapped in raw_scores:
            if float(score) > raw_scores[mapped]: 
                raw_scores[mapped] = float(score)
            
    total = sum(raw_scores.values())
    if total <= 0: return {g: 0.0 for g in ALL_KEYS}
    return {g: (v / total) * 100.0 for g, v in raw_scores.items()}

def infer_mood(tags, scores):
    mood_scores = {'happy': 0.0, 'sad': 0.0, 'energetic': 0.0, 'relaxed': 0.0}
    try:
        from genres_moods import map_tag_to_mood
        for tag, score in zip(tags, scores):
            m = map_tag_to_mood(str(tag))
            if m and m in mood_scores:
                if float(score) > mood_scores[m]: mood_scores[m] = float(score)
    except Exception: pass
    total = sum(mood_scores.values())
    if total > 0:
        best = max(mood_scores.items(), key=lambda x: x[1])
        return best[0], (best[1] / total * 100), mood_scores
    return "desconocido", 0.0, mood_scores

def analyze_audio(audio_path):
    global AST_LOAD_ERROR
    musicnn_tags, musicnn_scores = [], []
    try:
        from musicnn.extractor import extractor
        import numpy as np
        taggram, all_tags = extractor(audio_path, model="MSD_musicnn", input_length=3, extract_features=False)
        tags_mean = np.mean(taggram, axis=0)
        indices = tags_mean.argsort()[::-1][:50]
        musicnn_tags = [all_tags[i].lower() for i in indices]
        musicnn_scores = [float(tags_mean[i]) for i in indices]
    except Exception: pass

    ast_tags, ast_scores = [], []
    try:
        import torch
        model = get_ast_model()
        if model:
            import librosa
            import numpy as np
            y, _ = librosa.load(audio_path, sr=16000, duration=10.0)
            S = librosa.feature.melspectrogram(y=y, sr=16000, n_mels=128, fmin=0, fmax=8000, n_fft=400, hop_length=160)
            log_S = librosa.power_to_db(S, ref=np.max)
            if log_S.shape[1] > 1024: log_S = log_S[:, :1024]
            else: log_S = np.pad(log_S, ((0, 0), (0, 1024 - log_S.shape[1])), mode='constant')
            
            inputs = torch.tensor(log_S.T).unsqueeze(0).float()
            with torch.no_grad():
                logits = model(inputs).logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
            
            # ITERACIÓN SEGURA SOBRE id2label
            id2label = model.config.id2label
            probs_flat = probs[0].cpu().numpy()
            for idx_str, label in id2label.items():
                idx = int(idx_str)
                if idx < len(probs_flat):
                    ast_tags.append(str(label).lower())
                    ast_scores.append(float(probs_flat[idx]) * 5.0)
            AST_LOAD_ERROR = "¡Dataset Cargado con éxito!"
    except Exception as e:
        AST_LOAD_ERROR = f"Fallo en inferencia: {e}"

    genres_pct = aggregate_genre_percentages(musicnn_tags + ast_tags, musicnn_scores + ast_scores)
    mood, conf, m_scores = infer_mood(musicnn_tags, musicnn_scores)
    return {'success': True, 'genres_percent': genres_pct, 'mood': mood, 'mood_confidence': conf, 'm_scores': m_scores, 'load_info': AST_LOAD_ERROR}

@login_required
def index(request):
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                analysis = AudioAnalysis(audio_file=form.cleaned_data['audio_file'])
                analysis.save()
                results = analyze_audio(analysis.audio_file.path)
                analysis.genres_percent = results['genres_percent']
                analysis.mood = results['mood']
                analysis.mood_confidence = results['mood_confidence']
                analysis.save()
                messages.info(request, f"Estado del Dataset: {results['load_info']}")
                return redirect('analyzer:results', analysis_id=analysis.id)
            except Exception as e: messages.error(request, f"Error: {e}")
    else: form = AudioUploadForm()
    return render(request, 'analyzer/index.html', {'form': form})

@login_required
def results(request, analysis_id):
    analysis = get_object_or_404(AudioAnalysis, id=analysis_id)
    return render(request, 'analyzer/results.html', {
        'analysis': analysis, 
        'top_genres': analysis.get_top_genres(),
        'mood_confidence_display': int(analysis.mood_confidence)
    })

@login_required
def api_results(request, analysis_id):
    analysis = get_object_or_404(AudioAnalysis, id=analysis_id)
    return JsonResponse({'id': analysis.id, 'genres': analysis.genres_percent, 'mood': analysis.mood})
