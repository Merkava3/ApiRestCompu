"""
Script de inicio simple para el servidor Flask con WebSocket.
Ejecutar desde la raíz del proyecto: python start_server.py
"""
from api.app import create_app

if __name__ == "__main__":
    app = create_app()
    print("\n" + "="*60)
    print("🚀 Servidor Flask iniciado correctamente")
    print("="*60)
    print(f"📍 API REST: http://localhost:5000/api/v1")
    print(f"💬 WebSocket Chat: ws://localhost:5000/chat")
    print(f"🔍 Health Check: http://localhost:5000/api/v1/health")
    print("="*60 + "\n")
    
    # Iniciar servidor con soporte para WebSocket
    app.run(
        host='0.0.0.0',  # Escuchar en todas las interfaces
        port=5000,
        debug=True,
        threaded=True
    )
