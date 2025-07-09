#!/usr/bin/env python3
"""
Script simples de inicialização do servidor
"""

import uvicorn
import socket

def get_local_ip():
    """Obtém o IP local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    
    print("🚀 Iniciando servidor...")
    print(f"📍 IP: {local_ip}")
    print(f"🌐 URL: http://{local_ip}:8001")
    print(f"🏠 Local: http://localhost:8001")
    print("=" * 40)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 