#!/usr/bin/env python3
"""
Script URGENTE para limpar credenciais do histórico do Git
ATENÇÃO: Este script irá reescrever o histórico do Git
"""

import subprocess
import sys
import os

def executar_comando(comando):
    """Executa um comando e retorna o resultado"""
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    except Exception as e:
        return False, "", str(e)

def limpar_historico_git():
    """Limpa credenciais do histórico do Git"""
    print("🚨 LIMPEZA URGENTE DO HISTÓRICO DO GIT")
    print("=" * 50)
    
    # 1. Verificar se estamos no repositório correto
    sucesso, stdout, stderr = executar_comando("git status")
    if not sucesso:
        print("❌ Erro: Não estamos em um repositório Git válido")
        return False
    
    print("✅ Repositório Git válido encontrado")
    
    # 2. Fazer backup do branch atual
    print("\n📦 Fazendo backup do branch atual...")
    sucesso, stdout, stderr = executar_comando("git branch backup-antes-limpeza")
    if sucesso:
        print("✅ Backup criado: backup-antes-limpeza")
    else:
        print("⚠️ Aviso: Não foi possível criar backup")
    
    # 3. Limpar credenciais do histórico
    print("\n🧹 Limpando credenciais do histórico...")
    
    # Comando para remover credenciais do histórico
    comando_limpeza = '''
    git filter-branch --force --index-filter \
    "git ls-files -z | xargs -0 sed -i 's/Define@4536#8521/[REDACTED]/g'" \
    --prune-empty --tag-name-filter cat -- --all
    '''
    
    print("Executando limpeza...")
    sucesso, stdout, stderr = executar_comando(comando_limpeza)
    
    if sucesso:
        print("✅ Limpeza do histórico concluída")
    else:
        print("❌ Erro na limpeza do histórico")
        print("Erro:", stderr)
        return False
    
    # 4. Forçar garbage collection
    print("\n🗑️ Executando garbage collection...")
    sucesso, stdout, stderr = executar_comando("git reflog expire --expire=now --all")
    sucesso2, stdout2, stderr2 = executar_comando("git gc --prune=now --aggressive")
    
    if sucesso and sucesso2:
        print("✅ Garbage collection concluído")
    else:
        print("⚠️ Aviso: Garbage collection pode ter falhado")
    
    # 5. Verificar se ainda há credenciais
    print("\n🔍 Verificando se ainda há credenciais...")
    sucesso, stdout, stderr = executar_comando('git log -p --all | findstr "Define@4536"')
    
    if "Define@4536" in stdout:
        print("❌ ATENÇÃO: Ainda há credenciais no histórico!")
        print("Executando limpeza adicional...")
        
        # Limpeza adicional mais agressiva
        comando_adicional = '''
        git filter-branch --force --index-filter \
        "git ls-files -z | xargs -0 sed -i 's/Define@4536#8521/[CREDENTIALS_REMOVED]/g'" \
        --prune-empty --tag-name-filter cat -- --all
        '''
        
        sucesso, stdout, stderr = executar_comando(comando_adicional)
        if sucesso:
            print("✅ Limpeza adicional concluída")
        else:
            print("❌ Falha na limpeza adicional")
    else:
        print("✅ Nenhuma credencial encontrada no histórico")
    
    print("\n" + "=" * 50)
    print("🎉 LIMPEZA CONCLUÍDA!")
    print("\n⚠️ PRÓXIMOS PASSOS OBRIGATÓRIOS:")
    print("1. Force push para o repositório remoto:")
    print("   git push origin main --force")
    print("2. Notifique todos os colaboradores para clonar novamente")
    print("3. Delete o branch de backup local:")
    print("   git branch -D backup-antes-limpeza")
    
    return True

if __name__ == "__main__":
    print("🚨 ATENÇÃO: Este script irá reescrever o histórico do Git!")
    print("Isso pode afetar outros colaboradores do projeto.")
    
    resposta = input("\nDeseja continuar? (digite 'SIM' para confirmar): ")
    
    if resposta.upper() == "SIM":
        limpar_historico_git()
    else:
        print("Operação cancelada pelo usuário.")
        sys.exit(1) 