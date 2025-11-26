# 📝 Notas sobre Dependencias - VeviMaster-IA

## ⚠️ Problema de Compatibilidad con musicnn

### El Problema

La librería `musicnn` (versión 0.1.0, última disponible en PyPI desde 2019) tiene requisitos de dependencias muy específicos y antiguos:

- **numpy**: `>=1.14.5,<1.17` (versiones de 2018-2019)
- **tensorflow**: `>=2.0,<=2.0.4` (versión de 2019)
- **Python**: Compatible solo con Python 3.6-3.8

Esto crea conflictos con versiones más modernas de estas librerías y con Python 3.11.

### La Solución Aplicada

Hemos configurado el `Dockerfile` y `requirements.txt` para usar versiones compatibles con `musicnn`:

**Dockerfile:**
```dockerfile
# Usar Python 3.8 en lugar de 3.11
FROM ubuntu:22.04
RUN apt-get install python3.8 python3.8-dev ...
```

**requirements.txt:**
```txt
numpy>=1.14.5,<1.17
scipy>=1.2.0,<1.6
soundfile>=0.10.0
librosa==0.8.1
tensorflow==2.0.4
musicnn==0.1.0
```

**Ventajas:**
- ✓ Todas las dependencias son compatibles entre sí
- ✓ La funcionalidad de análisis de audio funciona correctamente
- ✓ Build de Docker exitoso
- ✓ Python 3.8 es estable y soportado hasta 2024

**Desventajas:**
- ⚠️ Usamos Python 3.8 en lugar de 3.11 (más antiguo)
- ⚠️ Usamos versiones antiguas de numpy y tensorflow
- ⚠️ Posibles vulnerabilidades de seguridad en versiones antiguas
- ⚠️ No podemos usar features más recientes de Python o TensorFlow

### Alternativas Futuras

Si necesitas actualizar las dependencias en el futuro, considera estas opciones:

#### Opción 1: Migrar a essentia

[Essentia](https://essentia.upf.edu/) es una librería más moderna para análisis de audio:

```python
# Reemplazar musicnn con essentia
pip install essentia-tensorflow

# Código de ejemplo
import essentia.standard as es
from essentia.tensorflow.models import TempoCNN

audio = es.MonoLoader(filename='audio.mp3')()
model = TempoCNN()
predictions = model(audio)
```

**Ventajas:**
- ✓ Activamente mantenida
- ✓ Compatible con TensorFlow moderno
- ✓ Más features y modelos disponibles

**Desventajas:**
- ⚠️ Requiere reescribir el código de análisis
- ⚠️ API diferente a musicnn

#### Opción 2: Usar musicnn desde GitHub

Existe un fork más reciente de musicnn en GitHub que podría ser compatible con versiones más nuevas:

```txt
# En requirements.txt
git+https://github.com/jordipons/musicnn.git@master
```

**Ventajas:**
- ✓ Código más reciente
- ✓ Posiblemente compatible con TensorFlow más nuevo

**Desventajas:**
- ⚠️ No está en PyPI (menos estable)
- ⚠️ No garantiza compatibilidad con TF 2.15+

#### Opción 3: Usar contenedores separados

Crear dos contenedores Docker:
1. **Contenedor principal**: Django con dependencias modernas
2. **Contenedor de análisis**: musicnn con dependencias antiguas

Comunicación vía API REST o colas de mensajes.

**Ventajas:**
- ✓ Mejor aislamiento de dependencias
- ✓ Puedes usar versiones modernas en el contenedor principal
- ✓ Escalabilidad independiente

**Desventajas:**
- ⚠️ Arquitectura más compleja
- ⚠️ Más recursos necesarios

## 🔒 Consideraciones de Seguridad

Las versiones antiguas de numpy y tensorflow pueden tener vulnerabilidades conocidas. Recomendaciones:

1. **Aislamiento**: Ejecuta siempre en contenedor Docker (ya implementado)
2. **Firewall**: Limita el acceso a la aplicación
3. **Actualizaciones**: Monitorea CVEs de las dependencias
4. **Migración**: Planifica migrar a essentia o alternativas modernas

## 📊 Versiones Actuales

| Librería | Versión Usada | Última Versión | Notas |
|----------|---------------|----------------|-------|
| numpy | 1.16.x | 2.2.x | Limitada por musicnn |
| tensorflow | 2.0.4 | 2.18.x | Limitada por musicnn |
| scipy | 1.5.x | 1.16.x | Compatible |
| librosa | 0.8.1 | 0.11.x | Compatible con numpy antiguo |
| musicnn | 0.1.0 | 0.1.0 | Sin actualizaciones desde 2019 |
| Django | 5.2.x | 5.2.x | ✓ Actualizado |

## 🛠️ Solución de Problemas

### Error: "Cannot install musicnn and numpy because these package versions have conflicting dependencies"

**Causa**: Intentaste instalar versiones incompatibles de numpy.

**Solución**: Usa el `requirements.txt` actualizado con versiones compatibles.

### Error: "ImportError: cannot import name 'top_tags' from 'musicnn.tagger'"

**Causa**: musicnn no está instalado correctamente o falta tensorflow.

**Solución**:
```bash
pip install tensorflow==2.0.4
pip install musicnn==0.1.0
```

### Advertencia: "Your CPU supports instructions that this TensorFlow binary was not compiled to use"

**Causa**: TensorFlow 2.0.4 no está optimizado para tu CPU.

**Solución**: Es solo una advertencia, puedes ignorarla. Si quieres deshabilitarla:
```python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

## 📅 Historial de Cambios

### 2025-11-24
- **Problema identificado**: Conflicto entre musicnn 0.1.0 y numpy/tensorflow modernos
- **Solución aplicada**: Downgrade a tensorflow 2.0.4 y numpy <1.17
- **Resultado**: Build de Docker exitoso con todas las funcionalidades

## 🔗 Referencias

- [musicnn en PyPI](https://pypi.org/project/musicnn/)
- [musicnn en GitHub](https://github.com/jordipons/musicnn)
- [Essentia (alternativa moderna)](https://essentia.upf.edu/)
- [TensorFlow 2.0.4 Release Notes](https://github.com/tensorflow/tensorflow/releases/tag/v2.0.4)

---

**Última actualización**: 2025-11-24  
**Estado**: ✓ Funcional con limitaciones conocidas
