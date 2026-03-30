import os
import django
import sys

# Setup Django environment
app_dir = r"c:\Users\alfaswz\Desktop\vevi mastering ia django 31-7-25\VeviMaster-IA\vevi_mastering"
sys.path.insert(0, app_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vevi_mastering.settings')
django.setup()

from analyzer.models import AudioAnalysis
from analyzer.views import analyze_audio

print("Reprocessing existing analyses...")
analyses = AudioAnalysis.objects.all()
for index, analysis in enumerate(analyses):
    audio_path = analysis.audio_file.path
    print(f"[{index+1}/{len(analyses)}] Processing {analysis.audio_file.name}...")
    
    if os.path.exists(audio_path):
        try:
            result = analyze_audio(audio_path)
            if result['success']:
                analysis.genres_percent = result['genres_percent']
                analysis.mood = result['mood']
                analysis.mood_confidence = result['mood_confidence']
                analysis.raw_tags = result['raw_tags']
                analysis.raw_scores = result['raw_scores']
                analysis.mood_scores = result['mood_scores']
                analysis.save()
                print("  -> Success!")
            else:
                print(f"  -> Failed: {result.get('error')}")
        except Exception as e:
            print(f"  -> Error: {e}")
    else:
        print(f"  -> File not found at {audio_path}")

print("Done re-processing data.")
