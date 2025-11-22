import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_JSON = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'resource', 'mastering_reference.json')

# Colores estilo FL Studio
COLORS = {
    'bg_dark': '#2b2b2b',
    'bg_medium': '#3c3c3c',
    'bg_light': '#4a4a4a',
    'accent': '#ff6b35',
    'accent_hover': '#ff8c5a',
    'text': '#ffffff',
    'text_dim': '#cccccc',
    'slider_bg': '#1e1e1e',
    'slider_fill': '#ff6b35',
    'knob': '#ff6b35',
    'knob_border': '#ffffff'
}

# Rango por defecto para sliders de parámetros globales y de banda
SLIDER_RANGES = {
    'loudness': (-60, 0),
    'loudness_range': (0, 30),
    'loudness_range_short': (0, 30),
    'peak': (0, 1),
    'rms': (-60, 0),
    'dynamics': (0, 10),
    'sharpness': (0, 10),
    'space': (-20, 20),
    'drr': (0, 30),
    'sample_rate': (8000, 192000),
    'channels': (1, 8),
    'high_freq': (20, 22000),
    'low_freq': (20, 22000),
    'mid_mean': (-60, 0),
    'mid_to_side_loudness': (-60, 0),
    'mid_to_side_loudness_range': (0, 30),
    'side_mean': (-60, 0),
}

# Presets embebidos
PRESETS = {
    'Pop': {
        'global': {
            'loudness': -8,
            'loudness_range': 6,
            'loudness_range_short': 8,
            'peak': 0.98,
            'rms': -10,
            'dynamics': 2.5,
            'sharpness': 2.2,
            'space': -3,
            'drr': 12,
            'sample_rate': 44100,
            'channels': 2,
        },
        'bands': [
            {'low_freq': 20, 'high_freq': 150, 'loudness': -18, 'loudness_range': 5, 'mid_mean': -15, 'mid_to_side_loudness': -10, 'mid_to_side_loudness_range': 10, 'side_mean': -25},
            {'low_freq': 150, 'high_freq': 400, 'loudness': -16, 'loudness_range': 6, 'mid_mean': -13, 'mid_to_side_loudness': -8, 'mid_to_side_loudness_range': 9, 'side_mean': -20},
            {'low_freq': 400, 'high_freq': 800, 'loudness': -17, 'loudness_range': 7, 'mid_mean': -14, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 8, 'side_mean': -18},
            {'low_freq': 800, 'high_freq': 1500, 'loudness': -18, 'loudness_range': 8, 'mid_mean': -15, 'mid_to_side_loudness': -6, 'mid_to_side_loudness_range': 7, 'side_mean': -17},
            {'low_freq': 1500, 'high_freq': 3000, 'loudness': -19, 'loudness_range': 8, 'mid_mean': -16, 'mid_to_side_loudness': -6, 'mid_to_side_loudness_range': 7, 'side_mean': -18},
            {'low_freq': 3000, 'high_freq': 6000, 'loudness': -20, 'loudness_range': 9, 'mid_mean': -17, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 8, 'side_mean': -20},
            {'low_freq': 6000, 'high_freq': 12000, 'loudness': -22, 'loudness_range': 10, 'mid_mean': -19, 'mid_to_side_loudness': -8, 'mid_to_side_loudness_range': 9, 'side_mean': -22},
            {'low_freq': 12000, 'high_freq': 20000, 'loudness': -25, 'loudness_range': 12, 'mid_mean': -22, 'mid_to_side_loudness': -10, 'mid_to_side_loudness_range': 10, 'side_mean': -25},
        ]
    },
    'Trap': {
        'global': {
            'loudness': -7,
            'loudness_range': 4,
            'loudness_range_short': 6,
            'peak': 0.99,
            'rms': -8,
            'dynamics': 1.8,
            'sharpness': 2.8,
            'space': -2,
            'drr': 10,
            'sample_rate': 44100,
            'channels': 2,
        },
        'bands': [
            {'low_freq': 20, 'high_freq': 120, 'loudness': -14, 'loudness_range': 4, 'mid_mean': -12, 'mid_to_side_loudness': -8, 'mid_to_side_loudness_range': 7, 'side_mean': -18},
            {'low_freq': 120, 'high_freq': 300, 'loudness': -13, 'loudness_range': 5, 'mid_mean': -11, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 6, 'side_mean': -16},
            {'low_freq': 300, 'high_freq': 800, 'loudness': -15, 'loudness_range': 6, 'mid_mean': -13, 'mid_to_side_loudness': -6, 'mid_to_side_loudness_range': 6, 'side_mean': -15},
            {'low_freq': 800, 'high_freq': 2000, 'loudness': -16, 'loudness_range': 7, 'mid_mean': -14, 'mid_to_side_loudness': -5, 'mid_to_side_loudness_range': 5, 'side_mean': -14},
            {'low_freq': 2000, 'high_freq': 5000, 'loudness': -18, 'loudness_range': 8, 'mid_mean': -16, 'mid_to_side_loudness': -6, 'mid_to_side_loudness_range': 6, 'side_mean': -16},
            {'low_freq': 5000, 'high_freq': 12000, 'loudness': -20, 'loudness_range': 9, 'mid_mean': -18, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 7, 'side_mean': -18},
            {'low_freq': 12000, 'high_freq': 20000, 'loudness': -23, 'loudness_range': 10, 'mid_mean': -21, 'mid_to_side_loudness': -9, 'mid_to_side_loudness_range': 8, 'side_mean': -22},
        ]
    },
    'Drill': {
        'global': {
            'loudness': -6,
            'loudness_range': 3,
            'loudness_range_short': 5,
            'peak': 0.99,
            'rms': -7,
            'dynamics': 1.5,
            'sharpness': 3.2,
            'space': -1,
            'drr': 9,
            'sample_rate': 44100,
            'channels': 2,
        },
        'bands': [
            {'low_freq': 20, 'high_freq': 100, 'loudness': -12, 'loudness_range': 3, 'mid_mean': -10, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 5, 'side_mean': -15},
            {'low_freq': 100, 'high_freq': 250, 'loudness': -11, 'loudness_range': 4, 'mid_mean': -9, 'mid_to_side_loudness': -6, 'mid_to_side_loudness_range': 5, 'side_mean': -13},
            {'low_freq': 250, 'high_freq': 600, 'loudness': -13, 'loudness_range': 5, 'mid_mean': -11, 'mid_to_side_loudness': -5, 'mid_to_side_loudness_range': 4, 'side_mean': -12},
            {'low_freq': 600, 'high_freq': 1500, 'loudness': -14, 'loudness_range': 6, 'mid_mean': -12, 'mid_to_side_loudness': -4, 'mid_to_side_loudness_range': 4, 'side_mean': -11},
            {'low_freq': 1500, 'high_freq': 4000, 'loudness': -16, 'loudness_range': 7, 'mid_mean': -14, 'mid_to_side_loudness': -5, 'mid_to_side_loudness_range': 5, 'side_mean': -13},
            {'low_freq': 4000, 'high_freq': 12000, 'loudness': -19, 'loudness_range': 8, 'mid_mean': -17, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 6, 'side_mean': -16},
            {'low_freq': 12000, 'high_freq': 20000, 'loudness': -22, 'loudness_range': 9, 'mid_mean': -20, 'mid_to_side_loudness': -8, 'mid_to_side_loudness_range': 7, 'side_mean': -20},
        ]
    },
    'Reggaeton': {
        'global': {
            'loudness': -7.5,
            'loudness_range': 5,
            'loudness_range_short': 7,
            'peak': 0.98,
            'rms': -9,
            'dynamics': 2.0,
            'sharpness': 2.5,
            'space': -2.5,
            'drr': 11,
            'sample_rate': 44100,
            'channels': 2,
        },
        'bands': [
            {'low_freq': 20, 'high_freq': 120, 'loudness': -15, 'loudness_range': 4, 'mid_mean': -13, 'mid_to_side_loudness': -9, 'mid_to_side_loudness_range': 8, 'side_mean': -20},
            {'low_freq': 120, 'high_freq': 300, 'loudness': -14, 'loudness_range': 5, 'mid_mean': -12, 'mid_to_side_loudness': -8, 'mid_to_side_loudness_range': 7, 'side_mean': -18},
            {'low_freq': 300, 'high_freq': 800, 'loudness': -16, 'loudness_range': 6, 'mid_mean': -14, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 7, 'side_mean': -17},
            {'low_freq': 800, 'high_freq': 2000, 'loudness': -17, 'loudness_range': 7, 'mid_mean': -15, 'mid_to_side_loudness': -6, 'mid_to_side_loudness_range': 6, 'side_mean': -16},
            {'low_freq': 2000, 'high_freq': 5000, 'loudness': -19, 'loudness_range': 8, 'mid_mean': -17, 'mid_to_side_loudness': -7, 'mid_to_side_loudness_range': 7, 'side_mean': -18},
            {'low_freq': 5000, 'high_freq': 12000, 'loudness': -21, 'loudness_range': 9, 'mid_mean': -19, 'mid_to_side_loudness': -8, 'mid_to_side_loudness_range': 8, 'side_mean': -20},
            {'low_freq': 12000, 'high_freq': 20000, 'loudness': -24, 'loudness_range': 10, 'mid_mean': -22, 'mid_to_side_loudness': -10, 'mid_to_side_loudness_range': 9, 'side_mean': -23},
        ]
    },
}

class RoundedFrame(tk.Frame):
    def __init__(self, master, corner_radius=10, padding=5, **kwargs):
        super().__init__(master, **kwargs)
        self.corner_radius = corner_radius
        self.padding = padding
        self.canvas = tk.Canvas(self, bg=COLORS['bg_dark'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.bind('<Configure>', self._draw_rounded_rect)

    def _draw_rounded_rect(self, event=None):
        self.canvas.delete('all')
        width = self.winfo_width()
        height = self.winfo_height()
        radius = self.corner_radius
        self.canvas.create_arc((0, 0, radius*2, radius*2), start=90, extent=90, fill=COLORS['bg_medium'], outline='')
        self.canvas.create_arc((width-radius*2, 0, width, radius*2), start=0, extent=90, fill=COLORS['bg_medium'], outline='')
        self.canvas.create_arc((0, height-radius*2, radius*2, height), start=180, extent=90, fill=COLORS['bg_medium'], outline='')
        self.canvas.create_arc((width-radius*2, height-radius*2, width, height), start=270, extent=90, fill=COLORS['bg_medium'], outline='')
        self.canvas.create_rectangle((radius, 0, width-radius, height), fill=COLORS['bg_medium'], outline='')
        self.canvas.create_rectangle((0, radius, width, height-radius), fill=COLORS['bg_medium'], outline='')

class GradientFrame(tk.Frame):
    def __init__(self, master, color1, color2, **kwargs):
        super().__init__(master, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind('<Configure>', self._draw_gradient)

    def _draw_gradient(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        gradient = tk.PhotoImage(width=width, height=height)
        line = "{{}} {{}} {{}}".format(self.color1, self.color2, self.color2)
        for y in range(height):
            gradient.put(line, (0, y))
        self.configure(background='')
        self.create_image((0, 0), image=gradient, anchor='nw')
        self.image = gradient

class RoundedButton(tk.Button):
    def __init__(self, master, text, command, radius=10, **kwargs):
        super().__init__(master, text=text, command=command, **kwargs)
        self.radius = radius
        self.configure(relief=tk.FLAT, bd=0, bg=COLORS['accent'], fg=COLORS['text'],
                       font=('Arial', 9, 'bold'), activebackground=COLORS['accent_hover'],
                       activeforeground=COLORS['text'])
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        self.config(bg=COLORS['accent_hover'])

    def on_leave(self, event):
        self.config(bg=COLORS['accent'])

class ProfessionalSlider(tk.Frame):
    def __init__(self, master, label, var, from_, to, resolution=0.1, **kwargs):
        super().__init__(master, bg=COLORS['bg_dark'], **kwargs)
        self.var = var
        self.from_ = from_
        self.to = to
        
        # Label
        self.label = tk.Label(self, text=label, bg=COLORS['bg_dark'], fg=COLORS['accent'], 
                             font=('Arial', 9, 'bold'))
        self.label.pack(pady=(5,2))
        
        # Slider container
        slider_frame = tk.Frame(self, bg=COLORS['bg_dark'])
        slider_frame.pack(pady=2)
        
        # Vertical slider with rounded style
        style = ttk.Style()
        style.configure('TScale', troughcolor=COLORS['slider_bg'], 
                        background=COLORS['bg_dark'], 
                        sliderthickness=15, 
                        relief='flat')
        self.slider = ttk.Scale(slider_frame, from_=from_, to=to, variable=var, 
                              orient=tk.VERTICAL, length=120, style='TScale')
        self.slider.pack(side='left', padx=5)
        
        # Value display
        self.value_label = tk.Label(slider_frame, text=str(round(var.get(), 2)), 
                                   bg=COLORS['bg_dark'], fg=COLORS['accent'],
                                   font=('Arial', 10, 'bold'), width=8)
        self.value_label.pack(side='left', padx=5)
        
        # Bind events
        self.slider.bind('<ButtonRelease-1>', self.update_display)
        self.var.trace_add('write', self.update_display)
        
        # Min/Max labels
        min_label = tk.Label(self, text=str(from_), bg=COLORS['bg_dark'], fg=COLORS['text_dim'],
                            font=('Arial', 7))
        min_label.pack()
        max_label = tk.Label(self, text=str(to), bg=COLORS['bg_dark'], fg=COLORS['text_dim'],
                            font=('Arial', 7))
        max_label.pack()
        
    def update_display(self, *args):
        value = round(self.var.get(), 2)
        self.value_label.config(text=str(value))
        
    def set_range(self, from_, to):
        self.from_ = from_
        self.to = to
        self.slider.config(from_=from_, to=to)

class MasteringGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('vevi mastering ia - Beta')
        self.geometry('1200x800')
        self.resizable(True, True)
        self.configure(bg=COLORS['bg_dark'])
        
        self.data = {}
        self.global_vars = {}
        self.slider_ranges = SLIDER_RANGES.copy()
        self.audio_file = None
        self.create_widgets()
        self.load_json(DEFAULT_JSON)

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self, bg=COLORS['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="VEVI MASTERING IA - BETA", 
                              bg=COLORS['bg_dark'], fg=COLORS['accent'],
                              font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Top section with presets and audio
        top_frame = tk.Frame(main_frame, bg=COLORS['bg_medium'])
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Presets section
        preset_frame = tk.LabelFrame(top_frame, text='PRESETS DE GÉNERO', 
                                   bg=COLORS['bg_medium'], fg=COLORS['accent'],
                                   font=('Arial', 10, 'bold'))
        preset_frame.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        
        for genre in PRESETS:
            btn = RoundedButton(preset_frame, text=genre, 
                              command=lambda g=genre: self.load_preset(g))
            btn.pack(side='left', padx=5, pady=5)
        
        # Audio section
        audio_frame = tk.LabelFrame(top_frame, text='ARCHIVO DE AUDIO', 
                                  bg=COLORS['bg_medium'], fg=COLORS['accent'],
                                  font=('Arial', 10, 'bold'))
        audio_frame.pack(side='right', fill='x', expand=True, padx=10, pady=10)
        
        self.audio_label = tk.Label(audio_frame, text='Ningún archivo seleccionado', 
                                  bg=COLORS['bg_medium'], fg=COLORS['text_dim'])
        self.audio_label.pack(side='left', padx=10)
        
        load_btn = RoundedButton(audio_frame, text='CARGAR AUDIO', 
                               command=self.load_audio)
        load_btn.pack(side='right', padx=10)
        
        # Middle section with sliders
        # Global parameters section directamente en main_frame
        global_label = tk.Label(main_frame, text='PARÁMETROS GLOBALES', 
                              bg=COLORS['bg_medium'], fg=COLORS['accent'],
                              font=('Arial', 12, 'bold'))
        global_label.pack(pady=(10, 0))
        # Sliders container with rounded frame directamente en main_frame
        sliders_frame = RoundedFrame(main_frame, bg=COLORS['bg_medium'])
        sliders_frame.pack(fill='x', padx=20, pady=(10, 0))
        self.global_sliders = {}
        slider_params = [
            ('loudness', 'LOUDNESS'),
            ('loudness_range', 'LOUDNESS RANGE'),
            ('loudness_range_short', 'LOUDNESS RANGE SHORT'),
            ('peak', 'PEAK'),
            ('rms', 'RMS'),
            ('dynamics', 'DYNAMICS'),
            ('sharpness', 'SHARPNESS'),
            ('space', 'SPACE'),
            ('drr', 'DRR'),
            ('sample_rate', 'SAMPLE RATE'),
            ('channels', 'CHANNELS'),
        ]
        for i, (key, label) in enumerate(slider_params):
            var = tk.DoubleVar()
            slider = ProfessionalSlider(sliders_frame, label, var,
                                 self.slider_ranges.get(key, (0, 1))[0],
                                 self.slider_ranges.get(key, (0, 1))[1],
                                 resolution=0.1, height=250)
            slider.pack(side='left', padx=10, pady=10, expand=True, fill='y')
            self.global_sliders[key] = (var, slider)
        
        # Configure grid weights
        for i in range(4):
            sliders_frame.columnconfigure(i, weight=1)
        
        # Bottom section with controls
        bottom_frame = tk.Frame(main_frame, bg=COLORS['bg_medium'])
        bottom_frame.pack(fill='x', pady=(0, 10))
        
        # Control buttons
        controls_frame = tk.Frame(bottom_frame, bg=COLORS['bg_medium'])
        controls_frame.pack(pady=10)
        
        RoundedButton(controls_frame, text='CARGAR JSON', 
                     command=self.load_json_dialog).pack(side='left', padx=5)
        RoundedButton(controls_frame, text='GUARDAR JSON', 
                     command=self.save_json_dialog).pack(side='left', padx=5)
        RoundedButton(controls_frame, text='EDITAR BANDAS', 
                     command=self.edit_bands_window).pack(side='left', padx=5)
        RoundedButton(controls_frame, text='CONFIGURAR SLIDERS', 
                     command=self.configure_sliders_window).pack(side='left', padx=5)
        
        # Barra de progreso y estado justo encima del botón de masterización
        progress_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        progress_frame.pack(fill='x', pady=(10, 0))
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', style='TProgressbar')
        self.progress.pack(fill='x', pady=5, padx=100)
        self.status_label = tk.Label(progress_frame, text='LISTO', bg=COLORS['bg_dark'], fg=COLORS['accent'], font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=(0, 5))
        # Botón de masterización grande y centrado, justo debajo de la barra de progreso
        apply_master_button = RoundedButton(main_frame, text='APLICAR MASTERIZACIÓN', 
                                            command=self.apply_mastering, 
                                            font=('Arial', 16, 'bold'), width=30, height=2)
        apply_master_button.pack(pady=10)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TProgressbar', 
                       troughcolor=COLORS['slider_bg'],
                       background=COLORS['accent'],
                       bordercolor=COLORS['bg_medium'])

        # Copyright label at the bottom
        copyright_label = tk.Label(self, text="© 2025 vevi a los mandos", bg=COLORS['bg_dark'], fg=COLORS['text_dim'], font=('Arial', 9))
        copyright_label.pack(side='bottom', pady=(0, 5))

    def load_audio(self):
        file_path = filedialog.askopenfilename(
            title='Seleccionar archivo de audio',
            filetypes=[
                ('Archivos de audio', '*.wav *.mp3 *.flac *.aiff'),
                ('Archivos WAV', '*.wav'),
                ('Todos los archivos', '*.*')
            ]
        )
        if file_path:
            self.audio_file = file_path
            self.audio_label.config(text=os.path.basename(file_path), fg=COLORS['text'])
            self.status_label.config(text=f'AUDIO CARGADO: {os.path.basename(file_path)}')

    def apply_mastering(self):
        if not self.audio_file:
            messagebox.showerror('Error', 'Primero debes cargar un archivo de audio.')
            return
        if not self.audio_file.lower().endswith('.wav'):
            messagebox.showerror('Error', 'Solo se aceptan archivos WAV para la masterización.')
            return
        
        # Generar nombre de salida automáticamente
        base_name = os.path.splitext(os.path.basename(self.audio_file))[0]
        suggested_name = f"{base_name}_vevi_master_ia.wav"
        output_dir = os.path.dirname(self.audio_file)
        output_path = os.path.join(output_dir, suggested_name)
        self.output_file = output_path
        
        # Ejecutar masterización en hilo separado
        self.progress.start()
        self.status_label.config(text='Procesando...')
        
        thread = threading.Thread(target=self._run_mastering, args=())
        thread.daemon = True
        thread.start()

    def _run_mastering(self):
        try:
            exe_path_exe = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'phaselimiter', 'bin', 'phase_limiter.exe')
            exe_path_noext = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'phaselimiter', 'bin', 'phase_limiter')
            exe_path = exe_path_exe if os.path.exists(exe_path_exe) else exe_path_noext
            if not os.path.exists(exe_path):
                # Listar archivos en la carpeta para depuración
                bin_dir = os.path.dirname(exe_path)
                try:
                    files_in_bin = os.listdir(bin_dir)
                except Exception as e:
                    files_in_bin = [f'Error al listar archivos: {e}']
                raise FileNotFoundError(f'No se encontró el ejecutable phase_limiter en: {exe_path_exe} ni {exe_path_noext}\n\nArchivos en bin: {files_in_bin}')
            cmd = [
                exe_path,
                f'-input={self.audio_file}',
                f'-output={self.output_file}'
            ]
            bin_dir = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'phaselimiter', 'bin')
            env = os.environ.copy()
            env['PATH'] = bin_dir + os.pathsep + env['PATH']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=BASE_DIR, env=env)
            
            if result.returncode == 0:
                self.mastered_file = self.output_file # Usar el archivo de salida solicitado
                self.after(0, lambda: self.progress.stop())
                self.after(0, lambda: self.status_label.config(text='MASTERIZACIÓN COMPLETADA'))
                self.after(0, lambda: messagebox.showinfo('Éxito', f'Audio masterizado guardado como:\n{os.path.basename(self.output_file)}'))
            else:
                error_msg = result.stderr if result.stderr else 'Error desconocido'
                self.after(0, lambda: self.progress.stop())
                self.after(0, lambda: self.status_label.config(text='Error en la masterización'))
                self.after(0, lambda: messagebox.showerror('Error', f'Error en la masterización:\n{error_msg}\n\nComando ejecutado:\n{cmd}'))
                
        except subprocess.TimeoutExpired:
            self.after(0, lambda: messagebox.showerror('Error', 'La masterización tardó demasiado tiempo'))
        except Exception as e:
            error_msg = str(e)
            exe_path = os.path.join(BASE_DIR, 'app_files', 'phaselimiter', 'phaselimiter', 'bin', 'phase_limiter.exe')
            self.after(0, lambda: self.progress.stop())
            self.after(0, lambda: self.status_label.config(text='Error en la masterización'))
            self.after(0, lambda: messagebox.showerror('Error', f'Error en la masterización:\n{error_msg}\n\nEjecutable: {exe_path}\nInput: {self.audio_file}\nOutput: {self.output_file}'))
        finally:
            self.after(0, lambda: self.status_label.config(text='LISTO'))
            
            # Limpiar archivo temporal
            # try:
            #     os.remove(config_file)
            # except:
            #     pass

    def save_mastered_audio(self):
        if not hasattr(self, 'mastered_file') or not os.path.exists(self.mastered_file):
            messagebox.showerror('Error', 'No hay audio masterizado para guardar. Primero aplica la masterización.')
            return
        
        save_path = filedialog.asksaveasfilename(
            title='Guardar audio masterizado',
            defaultextension='.wav',
            filetypes=[
                ('Archivos WAV', '*.wav'),
                ('Archivos MP3', '*.mp3'),
                ('Todos los archivos', '*.*')
            ],
            initialfilename=os.path.basename(self.mastered_file)
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(self.mastered_file, save_path)
                messagebox.showinfo('Éxito', f'Audio guardado en:\n{save_path}')
            except Exception as e:
                messagebox.showerror('Error', f'Error al guardar el archivo:\n{str(e)}')

    def load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            for key, (var, slider) in self.global_sliders.items():
                value = self.data.get(key, self.slider_ranges.get(key, (0, 1))[0])
                var.set(value)
            self.current_json = path
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo cargar el archivo JSON:\n{e}')

    def save_json(self, path):
        try:
            for key, (var, slider) in self.global_sliders.items():
                val = var.get()
                if key in ('channels', 'sample_rate'):
                    val = int(val)
                self.data[key] = val
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
            if path != 'temp_mastering_config.json':
                messagebox.showinfo('Guardado', 'Archivo JSON guardado correctamente.')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar el archivo JSON:\n{e}')

    def load_json_dialog(self):
        path = filedialog.askopenfilename(
            title='Seleccionar archivo JSON',
            filetypes=[('Archivos JSON', '*.json')],
            initialdir=os.path.dirname(DEFAULT_JSON)
        )
        if path:
            self.load_json(path)

    def save_json_dialog(self):
        path = filedialog.asksaveasfilename(
            title='Guardar archivo JSON',
            defaultextension='.json',
            filetypes=[('Archivos JSON', '*.json')],
            initialdir=os.path.dirname(DEFAULT_JSON)
        )
        if path:
            self.save_json(path)

    def load_preset(self, genre):
        preset = PRESETS[genre]
        # Globales
        for key, (var, slider) in self.global_sliders.items():
            value = preset['global'].get(key, self.slider_ranges.get(key, (0, 1))[0])
            var.set(value)
        # Bandas
        self.data['bands'] = [band.copy() for band in preset['bands']]
        messagebox.showinfo('Preset', f'Preset {genre} cargado. Puedes editar las bandas si lo deseas.')

    def edit_bands_window(self):
        # Create a new window for editing bands
        bands_window = tk.Toplevel(self)
        bands_window.title('Editar Bandas')
        bands_window.geometry('600x400')
        bands_window.configure(bg=COLORS['bg_dark'])

        # Create a frame for sliders
        bands_frame = tk.Frame(bands_window, bg=COLORS['bg_dark'])
        bands_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Example band parameters
        band_params = [
            ('LOW_FREQ', 'Low Frequency'),
            ('HIGH_FREQ', 'High Frequency'),
            ('LOUDNESS', 'Loudness'),
            ('LOUDNESS_RANGE', 'Loudness Range'),
            ('MID_MEAN', 'Mid Mean'),
            ('TO_SIDE_LOUDNESS', 'To Side Loudness'),
            ('SIDE_LOUDNESS', 'Side Loudness'),
            ('SIDE_MEAN', 'Side Mean'),
        ]

        # Create sliders for each band parameter
        for i, (key, label) in enumerate(band_params):
            var = tk.DoubleVar()
            slider = ProfessionalSlider(bands_frame, label, var, 0, 100)
            slider.pack(side='top', fill='x', padx=5, pady=5)

        # Add a button to save changes
        save_button = RoundedButton(bands_window, text='Guardar Cambios', command=bands_window.destroy)
        save_button.pack(pady=10)

    def configure_sliders_window(self):
        ConfigSlidersWindow(self, self.slider_ranges, self.global_sliders)

class BandsEditor(tk.Toplevel):
    def __init__(self, parent, bands, slider_ranges):
        super().__init__(parent)
        self.title('Editar Bandas de Frecuencia')
        self.geometry('1200x600')
        self.configure(bg=COLORS['bg_dark'])
        
        self.bands = bands
        self.slider_ranges = slider_ranges
        
        # Title
        title_label = tk.Label(self, text="EDITOR DE BANDAS DE FRECUENCIA", 
                              bg=COLORS['bg_dark'], fg=COLORS['accent'],
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        self.create_table()
        
        # Buttons
        btn_frame = tk.Frame(self, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=10)
        
        RoundedButton(btn_frame, text='AGREGAR BANDA', 
                     command=self.add_band).pack(side='left', padx=5)
        RoundedButton(btn_frame, text='GUARDAR CAMBIOS', 
                     command=self.save_changes).pack(side='left', padx=5)

    def create_table(self):
        columns = [
            'low_freq', 'high_freq', 'loudness', 'loudness_range',
            'mid_mean', 'mid_to_side_loudness', 'mid_to_side_loudness_range', 'side_mean'
        ]
        self.rows = []
        
        # Container
        container = tk.Frame(self, bg=COLORS['bg_medium'], relief=tk.RAISED, bd=2)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Headers
        header_frame = tk.Frame(container, bg=COLORS['bg_medium'])
        header_frame.pack(fill='x', pady=5)
        
        for i, col in enumerate(columns):
            header = tk.Label(header_frame, text=col.upper(), 
                            bg=COLORS['bg_medium'], fg=COLORS['accent'],
                            font=('Arial', 9, 'bold'), width=12)
            header.grid(row=0, column=i, padx=2, pady=2)
        
        # Bands
        bands_frame = tk.Frame(container, bg=COLORS['bg_medium'])
        bands_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        for row_idx, band in enumerate(self.bands):
            row_widgets = []
            for col_idx, col in enumerate(columns):
                var = tk.DoubleVar(value=band.get(col, 0))
                from_, to = self.slider_ranges.get(col, (0, 1))
                
                # Slider
                slider = tk.Scale(bands_frame, from_=from_, to=to, variable=var, 
                                orient=tk.VERTICAL, length=100, width=12,
                                bg=COLORS['slider_bg'], fg=COLORS['text'],
                                highlightbackground=COLORS['bg_medium'],
                                troughcolor=COLORS['slider_bg'],
                                activebackground=COLORS['accent'],
                                relief=tk.FLAT, bd=0)
                slider.grid(row=row_idx*2+1, column=col_idx, padx=2, pady=2)
                
                # Entry
                entry = tk.Entry(bands_frame, width=10, bg=COLORS['bg_light'], 
                               fg=COLORS['text'], relief=tk.FLAT, bd=1)
                entry.grid(row=row_idx*2+2, column=col_idx, padx=2, pady=2)
                entry.insert(0, str(var.get()))
                
                # Bind events
                slider.bind('<ButtonRelease-1>', lambda e, v=var, ent=entry: ent.delete(0, tk.END) or ent.insert(0, str(round(v.get(), 3))))
                entry.bind('<Return>', lambda e, v=var, ent=entry: v.set(float(ent.get()) if ent.get() else 0))
                var.trace_add('write', lambda *a, v=var, ent=entry: ent.delete(0, tk.END) or ent.insert(0, str(round(v.get(), 3))))
                
                row_widgets.append((var, slider, entry))
            self.rows.append(row_widgets)

    def add_band(self):
        new_band = {'low_freq': 20, 'high_freq': 200, 'loudness': -20, 'loudness_range': 5, 'mid_mean': -18, 'mid_to_side_loudness': -10, 'mid_to_side_loudness_range': 10, 'side_mean': -25}
        self.bands.append(new_band)
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate
        title_label = tk.Label(self, text="EDITOR DE BANDAS DE FRECUENCIA", 
                              bg=COLORS['bg_dark'], fg=COLORS['accent'],
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        self.create_table()
        
        btn_frame = tk.Frame(self, bg=COLORS['bg_dark'])
        btn_frame.pack(pady=10)
        RoundedButton(btn_frame, text='AGREGAR BANDA', 
                     command=self.add_band).pack(side='left', padx=5)
        RoundedButton(btn_frame, text='GUARDAR CAMBIOS', 
                     command=self.save_changes).pack(side='left', padx=5)

    def save_changes(self):
        columns = ['low_freq', 'high_freq', 'loudness', 'loudness_range', 'mid_mean', 'mid_to_side_loudness', 'mid_to_side_loudness_range', 'side_mean']
        for i, row in enumerate(self.rows):
            for j, (var, slider, entry) in enumerate(row):
                self.bands[i][columns[j]] = var.get()
        self.destroy()

class ConfigSlidersWindow(tk.Toplevel):
    def __init__(self, parent, slider_ranges, global_sliders):
        super().__init__(parent)
        self.title('Configurar Rangos de Sliders')
        self.geometry('600x700')
        self.configure(bg=COLORS['bg_dark'])
        
        self.slider_ranges = slider_ranges
        self.global_sliders = global_sliders
        self.entries = {}
        
        # Title
        title_label = tk.Label(self, text="CONFIGURAR RANGOS DE SLIDERS", 
                              bg=COLORS['bg_dark'], fg=COLORS['accent'],
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Container
        container = tk.Frame(self, bg=COLORS['bg_medium'], relief=tk.RAISED, bd=2)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        row = 0
        for key in slider_ranges:
            # Parameter name
            param_label = tk.Label(container, text=key.upper(), 
                                 bg=COLORS['bg_medium'], fg=COLORS['text'],
                                 font=('Arial', 9, 'bold'))
            param_label.grid(row=row, column=0, padx=10, pady=5, sticky='w')
            
            # Min value
            min_var = tk.DoubleVar(value=slider_ranges[key][0])
            min_entry = tk.Entry(container, textvariable=min_var, width=10,
                               bg=COLORS['bg_light'], fg=COLORS['text'],
                               relief=tk.FLAT, bd=1)
            min_entry.grid(row=row, column=1, padx=5, pady=5)
            
            # Max value
            max_var = tk.DoubleVar(value=slider_ranges[key][1])
            max_entry = tk.Entry(container, textvariable=max_var, width=10,
                               bg=COLORS['bg_light'], fg=COLORS['text'],
                               relief=tk.FLAT, bd=1)
            max_entry.grid(row=row, column=2, padx=5, pady=5)
            
            self.entries[key] = (min_var, max_var)
            row += 1
        
        # Apply button
        RoundedButton(container, text='APLICAR CAMBIOS', 
                     command=self.apply_ranges).grid(row=row, column=0, columnspan=3, pady=20)
        
    def apply_ranges(self):
        for key, (min_var, max_var) in self.entries.items():
            self.slider_ranges[key] = (min_var.get(), max_var.get())
            if key in self.global_sliders:
                _, slider = self.global_sliders[key]
                slider.set_range(min_var.get(), max_var.get())
        messagebox.showinfo('Sliders', 'Rangos de sliders actualizados.')
        self.destroy()

if __name__ == '__main__':
    app = MasteringGUI()
    app.mainloop()