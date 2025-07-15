#!/usr/bin/env python3
# backup_banco_tarefa_windows.py
"""
Configura uma tarefa agendada no Windows para execução diária de backup às 03:20
Usa o Agendador de Tarefas do Windows (schtasks)
"""

import subprocess
import sys
import os
from pathlib import Path

def criar_tarefa_agendada():
    """Cria uma tarefa agendada no Windows"""
    
    # Caminhos
    script_dir = Path(__file__).parent.absolute()
    backup_script = script_dir / "backup_banco_de_dados.py"
    python_exe = sys.executable
    
    # Nome da tarefa
    nome_tarefa = "BackupBancoDiario"
    
    print("🗂️  Configurando tarefa agendada no Windows...")
    print(f"📁  Diretório: {script_dir}")
    print(f"🐍  Python: {python_exe}")
    print(f"📜  Script: {backup_script}")
    
    # Comando para criar a tarefa
    cmd_criar = [
        "schtasks", "/create",
        "/tn", nome_tarefa,
        "/tr", f'"{python_exe}" "{backup_script}"',
        "/sc", "daily",
        "/st", "03:20",
        "/sd", "01/01/2025",  # Data de início
        "/ru", "SYSTEM",  # Executa como sistema para não precisar de usuário logado
        "/rl", "HIGHEST",  # Nível mais alto de privilégios
        "/f"  # Força sobrescrever se já existir
    ]
    
    try:
        # Remove tarefa existente se houver
        subprocess.run(
            ["schtasks", "/delete", "/tn", nome_tarefa, "/f"],
            capture_output=True
        )
        
        # Cria nova tarefa
        resultado = subprocess.run(cmd_criar, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅  Tarefa agendada criada com sucesso!")
            print(f"⏰  Execução programada para todos os dias às 03:20")
            print(f"📝  Nome da tarefa: {nome_tarefa}")
            
            # Mostra informações da tarefa
            mostrar_info_tarefa(nome_tarefa)
            
        else:
            print(f"❌  Erro ao criar tarefa: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"❌  Exceção ao criar tarefa: {e}")
        return False
    
    return True

def mostrar_info_tarefa(nome_tarefa):
    """Mostra informações da tarefa criada"""
    try:
        resultado = subprocess.run(
            ["schtasks", "/query", "/tn", nome_tarefa, "/fo", "list"],
            capture_output=True, text=True
        )
        
        if resultado.returncode == 0:
            print("\n📋  Informações da tarefa:")
            for linha in resultado.stdout.split('\n'):
                if any(info in linha for info in ["Nome da tarefa", "Próxima execução", "Status", "Horário de início"]):
                    print(f"   {linha.strip()}")
        
    except Exception as e:
        print(f"⚠️   Não foi possível obter informações da tarefa: {e}")

def remover_tarefa_agendada():
    """Remove a tarefa agendada"""
    nome_tarefa = "BackupBancoDiario"
    
    try:
        resultado = subprocess.run(
            ["schtasks", "/delete", "/tn", nome_tarefa, "/f"],
            capture_output=True, text=True
        )
        
        if resultado.returncode == 0:
            print(f"✅  Tarefa '{nome_tarefa}' removida com sucesso!")
        else:
            print(f"❌  Erro ao remover tarefa: {resultado.stderr}")
            
    except Exception as e:
        print(f"❌  Exceção ao remover tarefa: {e}")

def verificar_tarefa():
    """Verifica se a tarefa existe e está ativa"""
    nome_tarefa = "BackupBancoDiario"
    
    try:
        resultado = subprocess.run(
            ["schtasks", "/query", "/tn", nome_tarefa],
            capture_output=True, text=True
        )
        
        if resultado.returncode == 0:
            print(f"✅  Tarefa '{nome_tarefa}' está configurada")
            mostrar_info_tarefa(nome_tarefa)
            return True
        else:
            print(f"❌  Tarefa '{nome_tarefa}' não encontrada")
            return False
            
    except Exception as e:
        print(f"❌  Erro ao verificar tarefa: {e}")
        return False

if __name__ == "__main__":
    print("🕐  Configurador de Backup Agendado")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        acao = sys.argv[1].lower()
        
        if acao == "criar":
            criar_tarefa_agendada()
        elif acao == "remover":
            remover_tarefa_agendada()
        elif acao == "verificar":
            verificar_tarefa()
        else:
            print("❌  Ação inválida. Use: criar, remover ou verificar")
    else:
        print("Escolha uma ação:")
        print("1. Criar tarefa agendada")
        print("2. Verificar tarefa existente")  
        print("3. Remover tarefa agendada")
        
        escolha = input("\nEscolha (1-3): ").strip()
        
        if escolha == "1":
            criar_tarefa_agendada()
        elif escolha == "2":
            verificar_tarefa()
        elif escolha == "3":
            remover_tarefa_agendada()
        else:
            print("❌  Escolha inválida")
