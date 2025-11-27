"""
Script para ejecutar la aplicación FastAPI
"""

import uvicorn
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Iniciando Personal Finance API...")
    print("Documentación disponible en: http://localhost:8000/docs")
    print("ReDoc disponible en: http://localhost:8000/redoc")
    print("Presiona Ctrl+C para detener el servidor")
    print("-" * 60)

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
