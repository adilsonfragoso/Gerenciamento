#!/usr/bin/env python3
# backup_banco_daemon.py
"""
Daemon silencioso para execução do agendador de backup.
Executa em background sem terminal visível.
"""

import sys
import os
import time
import subprocess
from pathlib import Path
import signal
import atexit

# Arquivo de PID para controle do processo
PID_FILE = Path(__file__).parent.parent / "logs" / "backup_banco_daemon.pid"
LOG_FILE = Path(__file__).parent.parent / "logs" / "backup_banco_daemon.log"

def write_pid():
    """Escreve o PID do processo atual"""
    PID_FILE.parent.mkdir(exist_ok=True)
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def remove_pid():
    """Remove o arquivo de PID"""
    if PID_FILE.exists():
        PID_FILE.unlink()

def is_running():
    """Verifica se o daemon já está rodando"""
    if not PID_FILE.exists():
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Verifica se o processo ainda existe
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        # Processo não existe, remove PID file órfão
        remove_pid()
        return False

def stop_daemon():
    """Para o daemon se estiver rodando"""
    if not PID_FILE.exists():
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        
        # Força término se ainda estiver rodando
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
            
        remove_pid()
        return True
    except (OSError, ValueError):
        remove_pid()
        return False

def start_daemon():
    """Inicia o daemon"""
    if is_running():
        return False, "Daemon já está rodando"
    
    # Registra funções de limpeza
    atexit.register(remove_pid)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
    
    write_pid()
    
    try:
        # Executa o agendador
        agendador_script = Path(__file__).parent / "backup_banco_agendador.py"
        
        with open(LOG_FILE, 'a', encoding='utf-8') as log:
            log.write(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - Iniciando daemon de backup\n")
            
            processo = subprocess.Popen(
                [sys.executable, str(agendador_script)],
                cwd=str(agendador_script.parent),
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Aguarda o processo
            processo.wait()
            
    except Exception as e:
        with open(LOG_FILE, 'a', encoding='utf-8') as log:
            log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Erro no daemon: {e}\n")
    finally:
        remove_pid()

def get_status():
    """Retorna o status do daemon"""
    if is_running():
        with open(PID_FILE, 'r') as f:
            pid = f.read().strip()
        return True, f"Daemon rodando (PID: {pid})"
    else:
        return False, "Daemon parado"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python backup_banco_daemon.py [start|stop|status|restart]")
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    if comando == "start":
        if is_running():
            print("Daemon já está rodando")
            sys.exit(1)
        else:
            start_daemon()
            
    elif comando == "stop":
        if stop_daemon():
            print("Daemon parado")
        else:
            print("Daemon não estava rodando")
            
    elif comando == "restart":
        stop_daemon()
        time.sleep(3)
        if not is_running():
            start_daemon()
            print("Daemon reiniciado")
        else:
            print("Erro ao reiniciar daemon")
            
    elif comando == "status":
        running, msg = get_status()
        print(msg)
        sys.exit(0 if running else 1)
        
    else:
        print("Comando inválido. Use: start, stop, status ou restart")
        sys.exit(1)
