#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar dependências necessárias para os scripts de automação
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala um pacote Python"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"SUCESSO: {package} instalado com sucesso!")
            return True
        else:
            print(f"ERRO: Erro ao instalar {package}")
            return False
    except subprocess.CalledProcessError:
        print(f"ERRO: Erro ao instalar {package}")
        return False

def main():
    print("=== Instalador de Dependências ===")
    print("Instalando pacotes necessários para os scripts de automação...")
    
    # Lista de dependências
    dependencies = [
        "selenium",
        "mysql-connector-python", 
        "requests",
        "webdriver-manager"  # Alternativa para gerenciar drivers automaticamente
    ]
    
    print("\nDependências a serem instaladas:")
    for dep in dependencies:
        print(f"  • {dep}")
    
    print("\nIniciando instalação...")
    
    success_count = 0
    falhas = []
    for package in dependencies:
        if install_package(package):
            success_count += 1
        else:
            falhas.append(package)
    
    print(f"\n=== Resumo ===")
    print(f"Pacotes instalados com sucesso: {success_count}/{len(dependencies)}")
    
    if success_count == len(dependencies):
        print("SUCESSO: Todas as dependências foram instaladas!")
        print("\nPróximos passos:")
        print("1. Execute o script de automação desejado")
        print("2. O ChromeDriver será baixado automaticamente na primeira execução")
        print("3. Certifique-se de que o Google Chrome está instalado")
    else:
        print("ERRO: Algumas dependências falharam na instalação")
        print("Tente executar manualmente:")
        for package in falhas:
            print(f"  pip install {package}")

if __name__ == "__main__":
    main() 