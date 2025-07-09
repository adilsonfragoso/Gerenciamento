@echo off

REM Gerenciador da API - Menu Simples (compatibilidade total com CMD)
title Gerenciador da API
color 0E

:menu
cls
echo ============================================
echo         GERENCIADOR DA API
echo ============================================
echo.
echo 1 - Iniciar API (Desenvolvimento)
echo 2 - Iniciar API (Producao)
echo 3 - Parar API
echo 4 - Reiniciar API (Desenvolvimento)
echo 5 - Verificar Status
echo 6 - Testar Conexao
echo 7 - Ver Logs
echo 8 - Abrir no Navegador
echo 0 - Sair
echo.
set /p opcao="Escolha uma opcao (0-8): "

if "%opcao%"=="1" goto dev
if "%opcao%"=="2" goto prod
if "%opcao%"=="3" goto stop
if "%opcao%"=="4" goto restart
if "%opcao%"=="5" goto status
if "%opcao%"=="6" goto test
if "%opcao%"=="7" goto logs
if "%opcao%"=="8" goto browser
if "%opcao%"=="0" goto sair

echo Opcao invalida! Digite um numero de 0 a 8.
timeout /t 2 >nul
goto menu

:dev
echo Iniciando API em modo desenvolvimento...
start "API - Desenvolvimento" uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
pause
goto menu

:prod
echo Iniciando API em modo producao...
start "API - Producao" uvicorn app.main:app --host 0.0.0.0 --port 8001
pause
goto menu

:stop
echo Parando API...
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| find "uvicorn"') do (
    taskkill /PID %%i /F >nul 2>&1
)
echo API parada.
pause
goto menu

:restart
echo Reiniciando API...
call :stop
timeout /t 2 >nul
call :dev
goto menu

:status
echo Processos Python ativos:
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
pause
goto menu

:test
echo Testando conexao com a API...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8001' -TimeoutSec 5; Write-Host 'API respondendo!'; Write-Host $r.StatusCode } catch { Write-Host 'API nao esta respondendo' }"
pause
goto menu

:logs
if exist "app.log" (
    powershell "Get-Content 'app.log' -Tail 20"
) else (
    echo Arquivo de log nao encontrado (app.log)
)
pause
goto menu

:browser
start http://localhost:8001
pause
goto menu

:sair
echo Obrigado por usar o Gerenciador da API!
timeout /t 2 >nul
exit 