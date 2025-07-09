#!/usr/bin/env python3
"""
Script de inicialização do servidor FastAPI
Configurado para rodar na porta 8001 e ser acessível por todos os dispositivos da rede
"""

import uvicorn
import socket
import os
import sys
import time

def get_local_ip():
    """Obtém o IP local da máquina para exibir na tela"""
    try:
        # Conecta a um endereço externo para descobrir o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_port_available(port):
    """Verifica se a porta está disponível"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def main():
    """Função principal para iniciar o servidor"""
    
    # Configurações do servidor
    HOST = "0.0.0.0"  # Permite acesso de qualquer IP
    PORT = 8001       # Porta fixa 8001
    
    # Verificar se a porta está disponível
    if not check_port_available(PORT):
        print(f"❌ Porta {PORT} está em uso!")
        print("💡 Execute: netstat -ano | findstr :8001")
        print("💡 Para matar o processo: taskkill /PID [PID] /F")
        sys.exit(1)
    
    # Obter IP local para exibição
    local_ip = get_local_ip()
    
    print("🚀 Iniciando servidor de Gerenciamento...")
    print(f"📍 IP Local: {local_ip}")
    print(f"🔌 Porta: {PORT}")
    print(f"🌐 Acessível em: http://{local_ip}:{PORT}")
    print(f"🏠 Local: http://localhost:{PORT}")
    print("=" * 50)
    print("⏳ Aguardando inicialização do servidor...")
    
    try:
        # Iniciar o servidor uvicorn com configurações mais detalhadas
        uvicorn.run(
            "app.main:app",
            host=HOST,
            port=PORT,
            reload=True,  # Recarrega automaticamente em desenvolvimento
            log_level="info",
            access_log=True,
            use_colors=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")
        print(f"💡 Verifique se não há outro processo usando a porta {PORT}")
        sys.exit(1)

if __name__ == "__main__":
    main() 