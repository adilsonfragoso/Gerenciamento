@echo off
title Alimentador de Premiacoes - Modo Oculto
echo ========================================
echo Iniciando alimentador de premiacoes...
echo ========================================

:: Mudar para o diretorio correto
cd /d "D:\Documentos\Workspace\Gerenciamento"

:: Verificar se o Python esta disponivel
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH
    echo Verifique se o Python esta instalado e configurado
    pause
    exit /b 1
)

:: Executar o script em modo oculto
echo Executando alimenta_premiados.py --oculto...
python alimenta_premiados.py --oculto

:: Verificar se executou com sucesso
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERRO: Falha na execucao do script
    echo ========================================
    echo Verifique o arquivo de log: alimenta_premiados_oculto.log
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo SUCESSO: Script executado com sucesso
    echo ========================================
    echo Logs salvos em: alimenta_premiados_oculto.log
)

:: Fechar automaticamente apos 3 segundos
timeout /t 3 >nul 