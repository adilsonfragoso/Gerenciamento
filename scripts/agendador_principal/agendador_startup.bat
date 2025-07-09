@echo off
title Agendador Rifas - Startup
cd /d "D:\Documentos\Workspace\Gerenciamento"

REM Aguardar 30 segundos para o sistema inicializar completamente
timeout /t 30 /nobreak >nul

REM Criar diretório de logs se não existir
if not exist "scripts\logs" mkdir "scripts\logs"

REM Log de inicialização
echo [%date% %time%] Agendador iniciado via startup >> "scripts\logs\agendador_startup.log"

:loop
REM Executar o agendador Python em modo completamente silencioso
start /min /wait pythonw "scripts\agendador_principal\agendador_principal_melhorado.py"

REM Log de execução
echo [%date% %time%] Agendador executado >> "scripts\logs\agendador_startup.log"

REM Aguardar 30 minutos em modo silencioso
timeout /t 1800 /nobreak >nul

REM Log de reinicialização
echo [%date% %time%] Reiniciando agendador >> "scripts\logs\agendador_startup.log"

REM Reiniciar automaticamente
goto loop 