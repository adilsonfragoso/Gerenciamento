@echo off
REM ========================================
REM Agendador Principal - Startup Automático
REM ========================================
REM Coloque este arquivo na pasta de startup do Windows:
REM Win+R -> shell:startup -> Cole este arquivo

REM Aguardar 30 segundos após o boot para garantir que o sistema estabilizou
echo Aguardando sistema estabilizar...
timeout /t 30 /nobreak >nul

REM Criar pasta de logs se não existir
if not exist "D:\Documentos\Workspace\Gerenciamento\scripts\logs" (
    mkdir "D:\Documentos\Workspace\Gerenciamento\scripts\logs"
)

REM Mudar para o diretório do projeto
cd /d "D:\Documentos\Workspace\Gerenciamento"

REM Log de inicialização
echo %date% %time% - Iniciando agendador via startup >> "scripts\logs\startup_agendador.log"

REM Executar o agendador em modo oculto usando pythonw
start /min pythonw "scripts\agendador_principal\agendador_oculto.pyw"

REM Log de confirmação
echo %date% %time% - Agendador iniciado com sucesso >> "scripts\logs\startup_agendador.log"

REM Fechar esta janela
exit
