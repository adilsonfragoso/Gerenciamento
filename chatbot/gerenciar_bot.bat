@echo off
chcp 65001 >nul
cls
cd /d "D:\Documentos\Workspace\chatbot"

:menu
echo.
echo =======================================
echo          GERENCIADOR BOT RELATORIO
echo =======================================
echo.
echo 1. Parar Bot
echo 2. Deletar Processo
echo 3. Listar Processos
echo 4. Ver Logs (Tempo Real)
echo 5. Iniciar Bot
echo 6. Reiniciar Bot
echo 7. Salvar Configuracao
echo 8. Monitor Visual (sem caracteres especiais)
echo 9. Sair
echo.
set /p opcao="Escolha uma opcao (1-9): "

if "%opcao%"=="1" goto parar
if "%opcao%"=="2" goto deletar
if "%opcao%"=="3" goto listar
if "%opcao%"=="4" goto logs_tempo_real
if "%opcao%"=="5" goto iniciar
if "%opcao%"=="6" goto reiniciar
if "%opcao%"=="7" goto salvar
if "%opcao%"=="8" goto monitor_simples
if "%opcao%"=="9" goto sair

echo Opcao invalida!
timeout /t 2 >nul
goto menu

:parar
echo Parando o bot...
pm2 stop BotRelatorio
pause
goto menu

:deletar
echo Deletando processo...
pm2 delete BotRelatorio
pause
goto menu

:listar
echo Listando processos...
pm2 list
pause
goto menu

:logs_tempo_real
echo.
echo === LOGS EM TEMPO REAL ===
echo Pressione Ctrl+C para voltar ao menu
echo.
pm2 logs BotRelatorio --lines 0 --timestamp --raw
goto menu

:iniciar
echo Iniciando o bot...
pm2 start chatbot_limpo.js --name "BotRelatorio" --log-type json --merge-logs
pause
goto menu

:reiniciar
echo Reiniciando o bot...
pm2 restart BotRelatorio
pause
goto menu

:salvar
echo Salvando configuracao...
pm2 save
pause
goto menu

:monitor_simples
echo.
echo === STATUS DO BOT ===
pm2 describe BotRelatorio
echo.
echo === ULTIMAS 20 LINHAS DE LOG ===
pm2 logs BotRelatorio --lines 20 --nostream
echo.
echo Pressione qualquer tecla para atualizar ou ESC para voltar...
pause >nul
goto monitor_simples

:sair
echo Saindo...
exit 