#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import os

def configurar_pm2_logs():
    """Configura PM2 para logs em tempo real sem buffer"""
    
    print("Configurando PM2 para logs em tempo real...")
    
    # Configuração do PM2 para o bot
    config_pm2 = {
        "name": "BotRelatorio",
        "script": "chatbot.js",
        "cwd": "D:\\Documentos\\Workspace\\chatbot",
        "interpreter": "node",
        "env": {
            "NODE_ENV": "production",
            "PYTHONUNBUFFERED": "1",
            "FORCE_COLOR": "0"
        },
        "log_type": "json",
        "merge_logs": True,
        "log_date_format": "YYYY-MM-DD HH:mm:ss",
        "out_file": "./logs/bot_output.log",
        "error_file": "./logs/bot_error.log",
        "log_file": "./logs/bot_combined.log",
        "pid_file": "./logs/bot.pid",
        "instances": 1,
        "exec_mode": "fork",
        "watch": False,
        "ignore_watch": ["node_modules", "logs"],
        "max_memory_restart": "500M",
        "kill_timeout": 5000,
        "wait_ready": True,
        "listen_timeout": 10000,
        "autorestart": True,
        "max_restarts": 10,
        "min_uptime": "10s"
    }
    
    # Cria diretório de logs se não existir
    logs_dir = "D:\\Documentos\\Workspace\\chatbot\\logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Diretorio de logs criado: {logs_dir}")
    
    # Salva configuração em arquivo
    config_file = "D:\\Documentos\\Workspace\\chatbot\\ecosystem.config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump({"apps": [config_pm2]}, f, indent=2)
    
    print(f"Configuracao salva em: {config_file}")
    
    # Para o processo atual se estiver rodando
    try:
        subprocess.run(["pm2", "stop", "BotRelatorio"], capture_output=True)
        subprocess.run(["pm2", "delete", "BotRelatorio"], capture_output=True)
        print("Processo anterior parado e removido")
    except:
        pass
    
    # Inicia com a nova configuração
    try:
        result = subprocess.run(
            ["pm2", "start", config_file],
            capture_output=True,
            text=True,
            cwd="D:\\Documentos\\Workspace\\chatbot"
        )
        
        if result.returncode == 0:
            print("Bot iniciado com configuracao otimizada!")
            print("Use 'pm2 logs BotRelatorio --lines 0' para logs em tempo real")
            print("Use 'pm2 monit' para monitoramento visual")
        else:
            print(f"Erro ao iniciar: {result.stderr}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    configurar_pm2_logs() 