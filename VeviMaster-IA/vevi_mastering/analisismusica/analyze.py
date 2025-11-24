import argparse
import json
import os
import sys
from typing import Dict, List, Tuple

from colorama import Fore, Style
from musicnn.tagger import top_tags

from genres_moods import (
    TARGET_GENRES,
    MOOD_CATEGORIES,
    map_genre_tag_to_target,
    map_tag_to_mood,
)


def ensure_audio_exists(path: str) -> None:
    if not os.path.isfile(path):
        print(f"{Fore.RED}Error:{Style.RESET_ALL} no se encontró el archivo de audio: {path}")
        sys.exit(1)


def predict_tags(audio_path: str, top_n: int = 50) -> Tuple[List[str], List[float]]:
    # musicnn soporta diferentes modelos: 'MTT_musicnn', 'MSD_musicnn' (MSD es más general)
    tags, scores = top_tags(audio_path, model="MSD_musicnn", topN=top_n)
    # 'scores' llega como lista de floats en [0,1]
    return tags, scores


def aggregate_genre_percentages(tags: List[str], scores: List[float]) -> Dict[str, float]:
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
    mood_scores: Dict[str, float] = {m: 0.0 for m in MOOD_CATEGORIES}
    for tag, score in zip(tags, scores):
        mood = map_tag_to_mood(tag)
        if mood is not None:
            mood_scores[mood] += float(score)

    # Elegir el mood con mayor puntuación
    best_mood = max(mood_scores.items(), key=lambda kv: kv[1])
    total = sum(mood_scores.values())
    confidence = 0.0 if total <= 0 else (best_mood[1] / total)
    return best_mood[0], confidence, mood_scores


def pretty_print_results(genres_pct: Dict[str, float], mood: str, mood_conf: float) -> None:
    print(f"{Fore.CYAN}Resultados del análisis:{Style.RESET_ALL}")
    print("")
    print(f"{Fore.YELLOW}20 géneros (porcentaje de coincidencia):{Style.RESET_ALL}")
    # Ordenar por porcentaje descendente
    for genre, pct in sorted(genres_pct.items(), key=lambda kv: kv[1], reverse=True):
        print(f" - {genre:10s}: {pct:6.2f}%")

    print("")
    print(f"{Fore.GREEN}Estado de ánimo más probable:{Style.RESET_ALL} {mood} ({mood_conf*100:.1f}%)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analiza música (género y estado de ánimo) con un modelo IA gratuito")
    parser.add_argument("--audio", required=True, help="Ruta del archivo de audio a analizar")
    parser.add_argument("--json", action="store_true", help="Devuelve salida JSON")
    parser.add_argument("--topN", type=int, default=50, help="Número de tags superiores a considerar (default: 50)")
    args = parser.parse_args()

    ensure_audio_exists(args.audio)

    try:
        tags, scores = predict_tags(args.audio, top_n=args.topN)
    except Exception as exc:
        print(f"{Fore.RED}Error al inferir tags con musicnn:{Style.RESET_ALL} {exc}")
        print("Sugerencia: asegúrate de tener FFmpeg instalado y en el PATH si el formato es comprimido (p. ej., MP3).")
        sys.exit(2)

    genres_pct = aggregate_genre_percentages(tags, scores)
    mood, mood_conf, mood_scores = infer_mood(tags, scores)

    result = {
        "audio": os.path.abspath(args.audio),
        "genres_percent": genres_pct,
        "mood": mood,
        "mood_confidence": mood_conf,
        "raw": {
            "tags": tags,
            "scores": scores,
            "mood_scores": mood_scores,
        },
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        pretty_print_results(genres_pct, mood, mood_conf)


if __name__ == "__main__":
    main()



