@echo off
title Sistema de Backup - Acesso Rapido
color 0A
cd /d "%~dp0"

echo ================================================================
echo          SISTEMA DE BACKUP DE BANCO DE DADOS
echo ================================================================
echo.
echo Acessando pasta backup_bd...
echo.

cd backup_bd
if %errorlevel%==0 (
    echo Executando controlador de backup...
    backup_banco_controle.bat
) else (
    echo ERRO: Pasta backup_bd nao encontrada!
    echo Verifique se a pasta existe no diretorio atual.
    pause
)

cd ..
