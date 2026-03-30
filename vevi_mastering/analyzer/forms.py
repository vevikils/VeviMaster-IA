from django import forms
import os


class AudioUploadForm(forms.Form):
    """Formulario para subir archivos de audio"""
    audio_file = forms.FileField(
        label='Archivo de Audio',
        help_text='Formatos soportados: MP3, WAV, OGG, M4A (máx. 50 MB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/*',
            'id': 'audio-file-input'
        })
    )
    
    def clean_audio_file(self):
        audio_file = self.cleaned_data.get('audio_file')
        if not audio_file:
            raise forms.ValidationError('Por favor, selecciona un archivo de audio.')
        
        # Validar extensión
        valid_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac']
        ext = os.path.splitext(audio_file.name)[1].lower()
        
        if ext not in valid_extensions:
            raise forms.ValidationError(
                f'Formato no soportado. Formatos válidos: {", ".join(valid_extensions)}'
            )
        
        # Validar tamaño (50 MB)
        if audio_file.size > 50 * 1024 * 1024:
            raise forms.ValidationError('El archivo es demasiado grande. Máximo 50 MB.')
        
        return audio_file

