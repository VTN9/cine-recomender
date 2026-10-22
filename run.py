"""
Script de inicio de CineMatch AI.
Abre automáticamente el navegador e inicia el servidor web local en el puerto 8000.
"""

import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.2)
    print("\nAbriendo CineMatch AI en tu navegador web...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("  🎬 CineMatch AI - Recomendador Local de Cine y Series")
    print("  Conectado con OpenRouter API")
    print("=" * 60)
    print("Servidor activo en: http://127.0.0.1:8000")
    print("Presiona Ctrl + C para detener el servidor.\n")
    
    # Lanzar hilo para abrir navegador
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor FastAPI con auto-recarga
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
