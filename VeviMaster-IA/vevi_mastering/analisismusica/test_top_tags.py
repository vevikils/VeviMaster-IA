"""Script para probar qué devuelve top_tags"""
import sys
import os

# Agregar el directorio raíz al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from musicnn.tagger import top_tags
import inspect

# Verificar la firma de la función
print("Firma de top_tags:")
print(inspect.signature(top_tags))
print("\nDocstring:")
print(top_tags.__doc__)

# Intentar llamar a la función con un archivo de prueba (si existe)
# Primero necesitamos verificar cómo se llama
print("\nTipo de retorno esperado:")
print(f"Retorna: {top_tags.__annotations__ if hasattr(top_tags, '__annotations__') else 'No tiene anotaciones'}")

