@echo off
REM Gerenciador do Agendador - Menu Simples (compatibilidade total com CMD)
title Gerenciador do Agendador
color 0E

:menu
cls
echo ============================================
echo       GERENCIADOR DO AGENDADOR
echo ============================================
echo.
echo 1 - Iniciar Agendador
echo 2 - Parar Agendador
echo 3 - Reiniciar Agendador
echo 4 - Ver Status Detalhado
echo 5 - Ver Logs
echo 6 - Verificar Processo
echo 7 - Limpar Arquivos Temporarios
echo 8 - Abrir Dashboard
echo 0 - Sair
echo.
set /p opcao="Escolha uma opcao (0-8): "

if "%opcao%"=="1" goto iniciar
if "%opcao%"=="2" goto parar
if "%opcao%"=="3" goto reiniciar
if "%opcao%"=="4" goto status
if "%opcao%"=="5" goto logs
if "%opcao%"=="6" goto verificar
if "%opcao%"=="7" goto limpar
if "%opcao%"=="8" goto dashboard
if "%opcao%"=="0" goto sair

echo Opcao invalida! Digite um numero de 0 a 8.
timeout /t 2 >nul
goto menu

:iniciar
echo Iniciando agendador...
start "Agendador" python scripts/agendador/agendador_servico.py
pause
goto menu

:parar
echo Parando agendador...
python scripts/agendador/controlador_agendador.py 2
pause
goto menu

:reiniciar
echo Reiniciando agendador...
python scripts/agendador/controlador_agendador.py 3
pause
goto menu

:status
echo Status detalhado do agendador:
if exist scripts/agendador/agendador_status.json (
    type scripts\agendador\agendador_status.json
) else (
    echo Arquivo de status nao encontrado.
)
pause
goto menu

:logs
echo Exibindo ultimas 20 linhas do log:
if exist scripts/agendador/logs/agendador_rifas.log (
    powershell "Get-Content 'scripts/agendador/logs/agendador_rifas.log' -Tail 20"
) else (
    echo Arquivo de log nao encontrado.
)
pause
goto menu

:verificar
echo Verificando se o processo do agendador esta rodando...
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | find "agendador_servico.py" >nul
if %errorlevel%==0 (
    echo Agendador esta rodando.
) else (
    echo Agendador NAO esta rodando.
)
pause
goto menu

:limpar
echo Limpando arquivos temporarios...
if exist temp_uploads (
    rmdir /s /q temp_uploads
    echo Pasta temp_uploads removida.
) else (
    echo Nenhum arquivo temporario encontrado.
)
pause
goto menu

:dashboard
start http://localhost:8001/dashboard
pause
goto menu

:sair
echo Obrigado por usar o Gerenciador do Agendador!
timeout /t 2 >nul
exit 