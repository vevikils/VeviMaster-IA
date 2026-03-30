import sys
import os
import json

sys.path.append('c:\\Users\\alfaswz\\Desktop\\vevi mastering ia django 31-7-25\\VeviMaster-IA\\vevi_mastering\\analisismusica\\.venv\\Lib\\site-packages')
sys.path.append('c:\\Users\\alfaswz\\Desktop\\vevi mastering ia django 31-7-25\\VeviMaster-IA\\vevi_mastering')

from genres_moods import TARGET_GENRES, normalize_tag, map_genre_tag_to_target

def analyze_logic(audio_path, top_n=50):
    from musicnn.extractor import extractor
    import numpy as np
    
    taggram, all_tags = extractor(audio_path, model="MSD_musicnn", input_length=3, input_overlap=False, extract_features=False)
    tags_likelihood_mean = np.mean(taggram, axis=0)
    
    sorted_indices = tags_likelihood_mean.argsort()[::-1]
    
    tags = [all_tags[i] for i in sorted_indices[:top_n]]
    scores = [float(tags_likelihood_mean[i]) for i in sorted_indices[:top_n]]
    
    tags = [t.lower() for t in tags]
    
    raw_scores = {g: 0.0 for g in TARGET_GENRES}
    for tag, score in zip(tags, scores):
        mapped = map_genre_tag_to_target(tag)
        if mapped is not None:
            current = raw_scores[mapped]
            if float(score) > current:
                raw_scores[mapped] = float(score)

    total = sum(raw_scores.values())
    if total <= 0:
        genres_pct = {g: 0.0 for g in TARGET_GENRES}
    else:
        genres_pct = {g: (v / total) * 100.0 for g, v in raw_scores.items()}
    
    return tags[:15], scores[:15], {k: v for k, v in genres_pct.items() if v > 0}

audio_dir = 'c:\\Users\\alfaswz\\Desktop\\vevi mastering ia django 31-7-25\\VeviMaster-IA\\vevi_mastering\\media\\audio_files'
if os.path.exists(audio_dir):
    files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3') or f.endswith('.wav')]
    if files:
        audio_file = os.path.join(audio_dir, files[0])
        try:
            tags, scores, pct = analyze_logic(audio_file)
            with open('c:\\Users\\alfaswz\\Desktop\\vevi mastering ia django 31-7-25\\VeviMaster-IA\\out.json', 'w') as f:
                json.dump({"tags": tags, "scores": scores, "pct": pct}, f)
        except Exception as e:
            print("ERROR", e)
