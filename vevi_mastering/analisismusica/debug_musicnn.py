
import sys
import os
from musicnn.tagger import top_tags

# Add current directory to path if needed, though not strictly necessary for this test
sys.path.append(os.getcwd())

audio_path = "c:/analisismusica/media/audio_files/NInfomana_-_vevi_._7_vevi_master_ia.wav"

print("Calling top_tags...")
try:
    result = top_tags(audio_path, model="MSD_musicnn", topN=10, print_tags=False)
    print(f"Type of result: {type(result)}")
    if isinstance(result, (tuple, list)):
        print(f"Length of result: {len(result)}")
        print(f"Tags: {result}")
    else:
        print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
