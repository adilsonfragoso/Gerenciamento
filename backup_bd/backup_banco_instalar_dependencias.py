#!/usr/bin/env python3
# backup_banco_instalar_dependencias.py
"""
Instala as dependências necessárias para o sistema de backup agendado
"""

import subprocess
import sys
import os

def instalar_dependencia(pacote):
    """Instala um pacote Python"""
    try:
        print(f"📦  Instalando {pacote}...")
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", pacote],
            capture_output=True, text=True
        )
        
        if resultado.returncode == 0:
            print(f"✅  {pacote} instalado com sucesso!")
            return True
        else:
            print(f"❌  Erro ao instalar {pacote}: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"❌  Exceção ao instalar {pacote}: {e}")
        return False

def verificar_dependencia(pacote):
    """Verifica se um pacote está instalado"""
    try:
        __import__(pacote)
        print(f"✅  {pacote} já instalado")
        return True
    except ImportError:
        print(f"❌  {pacote} não instalado")
        return False

def main():
    """Instala todas as dependências necessárias"""
    print("🚀  Instalador de Dependências - Sistema de Backup")
    print("=" * 55)
    
    dependencias = [
        ("python-dotenv", "dotenv"),
        ("schedule", "schedule"),
    ]
    
    # Dependências opcionais para serviço Windows
    dependencias_windows = [
        ("pywin32", "win32serviceutil"),
    ]
    
    print("\n📋  Verificando dependências obrigatórias...")
    
    todas_ok = True
    for pacote_pip, pacote_import in dependencias:
        if not verificar_dependencia(pacote_import):
            if not instalar_dependencia(pacote_pip):
                todas_ok = False
    
    print("\n📋  Verificando dependências opcionais (Windows)...")
    for pacote_pip, pacote_import in dependencias_windows:
        if not verificar_dependencia(pacote_import):
            print(f"⚠️   {pacote_pip} não instalado (opcional para serviço Windows)")
            resposta = input(f"   Deseja instalar {pacote_pip}? (s/n): ").lower()
            if resposta in ['s', 'sim', 'y', 'yes']:
                instalar_dependencia(pacote_pip)
    
    print("\n" + "=" * 55)
    if todas_ok:
        print("✅  Todas as dependências obrigatórias estão instaladas!")
        print("\n🎯  Próximos passos:")
        print("   1. Execute: python backup_banco_tarefa_windows.py criar")
        print("   2. Ou use: python backup_banco_agendador.py (execução manual)")
    else:
        print("❌  Algumas dependências falharam na instalação")
        print("   Tente executar novamente ou instale manualmente")

if __name__ == "__main__":
    main()
