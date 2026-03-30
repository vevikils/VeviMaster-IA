from django.contrib import admin
from .models import AudioAnalysis


@admin.register(AudioAnalysis)
class AudioAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'audio_file_name', 'mood', 'mood_confidence', 'uploaded_at')
    list_filter = ('mood', 'uploaded_at')
    search_fields = ('audio_file', 'mood')
    readonly_fields = ('uploaded_at', 'genres_percent', 'mood', 'mood_confidence', 
                      'raw_tags', 'raw_scores', 'mood_scores')
    
    def audio_file_name(self, obj):
        return obj.audio_file.name.split('/')[-1]
    audio_file_name.short_description = 'Archivo'
    
    fieldsets = (
        ('Archivo', {
            'fields': ('audio_file', 'uploaded_at')
        }),
        ('Resultados', {
            'fields': ('mood', 'mood_confidence', 'genres_percent')
        }),
        ('Datos Raw', {
            'fields': ('raw_tags', 'raw_scores', 'mood_scores'),
            'classes': ('collapse',)
        }),
    )
