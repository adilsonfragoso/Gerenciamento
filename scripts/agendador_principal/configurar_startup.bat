@echo off
title Configurar Agendador no Startup
echo ===================================
echo    CONFIGURAR AGENDADOR NO STARTUP
echo ===================================
echo.

echo [INFO] Configurando agendador para iniciar automaticamente com o Windows...
echo.

REM Caminho completo do script de startup
set "startup_script=D:\Documentos\Workspace\Gerenciamento\scripts\agendador_principal\agendador_startup.bat"

REM Verificar se o arquivo existe
if not exist "%startup_script%" (
    echo [ERRO] Arquivo agendador_startup.bat nao encontrado!
    pause
    exit /b 1
)

echo [INFO] Opcoes disponiveis:
echo.
echo 1. Adicionar ao Startup do Usuario (Recomendado)
echo 2. Adicionar ao Startup do Sistema (Administrador)
echo 3. Remover do Startup
echo 4. Verificar Status
echo 5. Sair
echo.
set /p opcao="Escolha uma opcao (1-5): "

if "%opcao%"=="1" goto startup_usuario
if "%opcao%"=="2" goto startup_sistema
if "%opcao%"=="3" goto remover_startup
if "%opcao%"=="4" goto verificar_status
if "%opcao%"=="5" goto sair
goto menu

:startup_usuario
echo.
echo [INFO] Adicionando ao startup do usuario...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "AgendadorRifas" /t REG_SZ /d "\"%startup_script%\"" /f
if %errorlevel% equ 0 (
    echo [SUCESSO] Agendador adicionado ao startup do usuario!
    echo [INFO] O agendador iniciara automaticamente quando voce fizer login.
) else (
    echo [ERRO] Falha ao adicionar ao startup do usuario.
)
echo.
pause
goto menu

:startup_sistema
echo.
echo [INFO] Verificando privilegios de administrador...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Esta opcao requer privilegios de administrador.
    echo Execute este script como administrador.
    pause
    goto menu
)

echo [INFO] Adicionando ao startup do sistema...
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "AgendadorRifas" /t REG_SZ /d "\"%startup_script%\"" /f
if %errorlevel% equ 0 (
    echo [SUCESSO] Agendador adicionado ao startup do sistema!
    echo [INFO] O agendador iniciara automaticamente quando o Windows iniciar.
) else (
    echo [ERRO] Falha ao adicionar ao startup do sistema.
)
echo.
pause
goto menu

:remover_startup
echo.
echo [INFO] Removendo do startup...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "AgendadorRifas" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "AgendadorRifas" /f >nul 2>&1
echo [SUCESSO] Agendador removido do startup!
echo.
pause
goto menu

:verificar_status
echo.
echo [INFO] Verificando status do startup...
echo.

echo Startup do Usuario:
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "AgendadorRifas" >nul 2>&1
if %errorlevel% equ 0 (
    echo [STATUS] AgendadorRifas encontrado no startup do usuario
) else (
    echo [STATUS] AgendadorRifas NAO encontrado no startup do usuario
)

echo.
echo Startup do Sistema:
reg query "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "AgendadorRifas" >nul 2>&1
if %errorlevel% equ 0 (
    echo [STATUS] AgendadorRifas encontrado no startup do sistema
) else (
    echo [STATUS] AgendadorRifas NAO encontrado no startup do sistema
)

echo.
pause
goto menu

:sair
echo.
echo [INFO] Saindo...
exit /b 0 