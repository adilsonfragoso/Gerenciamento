@echo off
title Sistema de Backup Automatico - Controle
color 0A
cd /d "%~dp0"

:MENU
cls
echo ================================================================
echo          SISTEMA DE BACKUP AUTOMATICO - CONTROLE
echo ================================================================
echo.
echo 1. Iniciar servico de backup
echo 2. Parar servico de backup  
echo 3. Reiniciar servico de backup
echo 4. Verificar status do servico
echo 5. Executar backup manual (teste)
echo 6. Ver logs do sistema
echo 7. Configurar agendamento Windows
echo 8. Sair
echo.
echo ================================================================

set /p choice="Escolha uma opcao (1-8): "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto RESTART
if "%choice%"=="4" goto STATUS
if "%choice%"=="5" goto MANUAL
if "%choice%"=="6" goto LOGS
if "%choice%"=="7" goto SCHEDULE
if "%choice%"=="8" goto EXIT

echo Opcao invalida! Pressione qualquer tecla para continuar...
pause >nul
goto MENU

:START
echo.
echo Iniciando servico de backup...
python backup_banco_daemon.py start
if %errorlevel%==0 (
    echo Servico iniciado com sucesso!
) else (
    echo Erro ao iniciar servico ou ja estava rodando.
)
echo.
pause
goto MENU

:STOP
echo.
echo Parando servico de backup...
python backup_banco_daemon.py stop
echo Servico parado.
echo.
pause
goto MENU

:RESTART
echo.
echo Reiniciando servico de backup...
python backup_banco_daemon.py restart
echo Servico reiniciado.
echo.
pause
goto MENU

:STATUS
echo.
echo Verificando status do servico...
python backup_banco_daemon.py status
echo.
echo Verificando agendamento Windows...
schtasks /query /tn "BackupBancoDiario" /fo list 2>nul
if %errorlevel%==0 (
    echo Tarefa Windows configurada: OK
) else (
    echo Tarefa Windows: NAO CONFIGURADA
)
echo.
pause
goto MENU

:MANUAL
echo.
echo Executando backup manual para teste...
python backup_banco_de_dados.py
echo.
pause
goto MENU

:LOGS
echo.
echo Mostrando ultimas linhas dos logs...
echo.
echo ================ LOG GERAL AGENDADOR ================
if exist "..\scripts\andamento\logs\logs_geral_agendador.log" (
    powershell -command "Get-Content '..\scripts\andamento\logs\logs_geral_agendador.log' | Select-Object -Last 10"
) else (
    echo Arquivo de log nao encontrado.
)
echo.
echo ================ LOG DAEMON ================
if exist "..\logs\backup_banco_daemon.log" (
    powershell -command "Get-Content '..\logs\backup_banco_daemon.log' | Select-Object -Last 10"
) else (
    echo Arquivo de log nao encontrado.
)
echo.
pause
goto MENU

:SCHEDULE
echo.
echo Configurando agendamento no Windows...
python backup_banco_tarefa_windows.py criar
echo.
pause
goto MENU

:EXIT
echo.
echo Saindo...
exit /b 0
