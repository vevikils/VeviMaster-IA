from django.db import models
import json


class AudioAnalysis(models.Model):
    """Modelo para almacenar análisis de audio"""
    audio_file = models.FileField(upload_to='audio_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Resultados del análisis
    genres_percent = models.JSONField(default=dict, help_text="Porcentajes de géneros")
    mood = models.CharField(max_length=50, blank=True)
    mood_confidence = models.FloatField(default=0.0)
    
    # Datos raw
    raw_tags = models.JSONField(default=list, help_text="Tags detectados")
    raw_scores = models.JSONField(default=list, help_text="Scores de los tags")
    mood_scores = models.JSONField(default=dict, help_text="Scores de estados de ánimo")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Análisis de Audio'
        verbose_name_plural = 'Análisis de Audio'
    
    def __str__(self):
        return f"Análisis de {self.audio_file.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_top_genres(self, top_n=5):
        """Obtiene los top N géneros ordenados por porcentaje"""
        if not self.genres_percent:
            return []
        sorted_genres = sorted(
            self.genres_percent.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_genres[:top_n]
