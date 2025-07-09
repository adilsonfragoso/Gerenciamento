#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validação de links pendentes em `extracoes`

• Usa o mesmo `test_link()` que você já tem, sem alterar a lógica de detecção de erro
• Lê da tabela `extracoes` todos os registros com status='pendente'
• Testa cada URL em paralelo com Selenium headless
• Atualiza cada linha em `extracoes` para status='ok' ou status='error'
• Download automático do ChromeDriver compatível
• Fallback para webdriver-manager se necessário
"""

import datetime
import time
import os
import subprocess
import requests
import zipfile
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def get_chrome_version():
    """Obtém a versão do Chrome instalada no sistema"""
    try:
        if platform.system() == "Windows":
            # Windows - verifica no registro
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        elif platform.system() == "Darwin":  # macOS
            # macOS - verifica no Applications
            result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                  capture_output=True, text=True)
            return result.stdout.strip().split()[-1]
        else:  # Linux
            # Linux - verifica com comando
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            return result.stdout.strip().split()[-1]
    except Exception as e:
        print(f"Erro ao obter versão do Chrome: {e}")
        return None

def get_chromedriver_version(chrome_version):
    """Obtém a versão do ChromeDriver compatível com a versão do Chrome"""
    if not chrome_version:
        return None
    
    # Extrai versão major (ex: 137.0.7151.69 -> 137)
    major_version = int(chrome_version.split('.')[0])
    
    # Primeiro tenta a versão major exata
    try:
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            chromedriver_version = response.text.strip()
            print(f"SUCESSO: ChromeDriver encontrado: versão {chromedriver_version} (para Chrome {major_version})")
            return chromedriver_version
    except Exception as e:
        print(f"ERRO: Tentativa para versão major {major_version} falhou: {e}")
    
    # Se não encontrar, tenta versões major anteriores
    for version_to_try in range(major_version - 1, major_version - 10, -1):  # Tenta até 10 versões major anteriores
        try:
            # Consulta a API do ChromeDriver para obter a versão mais recente
            url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version_to_try}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                chromedriver_version = response.text.strip()
                print(f"SUCESSO: ChromeDriver encontrado: versão {chromedriver_version} (para Chrome {version_to_try})")
                return chromedriver_version
        except Exception as e:
            print(f"ERRO: Tentativa para versão major {version_to_try} falhou: {e}")
            continue
    
    print(f"ERRO: Não foi possível encontrar ChromeDriver compatível para Chrome {major_version}")
    return None

def get_chromedriver_version_improved(chrome_version):
    """Versão melhorada que tenta versões específicas dentro da mesma major version"""
    if not chrome_version:
        return None
    
    # Extrai componentes da versão (ex: 137.0.7151.69 -> [137, 0, 7151, 69])
    version_parts = chrome_version.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1]) if len(version_parts) > 1 else 0
    build = int(version_parts[2]) if len(version_parts) > 2 else 0
    patch = int(version_parts[3]) if len(version_parts) > 3 else 0
    
    print(f"Analisando versão Chrome: {major}.{minor}.{build}.{patch}")
    
    # 1. Primeiro tenta a versão major exata
    try:
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            chromedriver_version = response.text.strip()
            print(f"SUCESSO: ChromeDriver encontrado: versão {chromedriver_version} (para Chrome {major})")
            return chromedriver_version
    except Exception as e:
        print(f"ERRO: Tentativa para versão major {major} falhou: {e}")
    
    # 2. Tenta versões específicas da mesma major version (build anterior)
    # Exemplo: para 137.0.7151.69, tenta 137.0.7151.68, 137.0.7151.67, etc.
    for patch_try in range(patch - 1, max(0, patch - 5), -1):  # Tenta até 5 patches anteriores
        try:
            specific_version = f"{major}.{minor}.{build}.{patch_try}"
            url = f"https://storage.googleapis.com/chrome-for-testing-public/{specific_version}/win32/chromedriver-win32.zip"
            response = requests.head(url, timeout=10)  # Usa HEAD para verificar se existe
            if response.status_code == 200:
                print(f"SUCESSO: ChromeDriver encontrado para versão específica: {specific_version}")
                return specific_version
        except Exception as e:
            print(f"ERRO: Tentativa para versão específica {major}.{minor}.{build}.{patch_try} falhou")
            continue
    
    # 3. Tenta builds anteriores da mesma major version
    # Exemplo: para 137.0.7151.69, tenta 137.0.7150.xxx, 137.0.7149.xxx, etc.
    for build_try in range(build - 1, max(0, build - 10), -1):  # Tenta até 10 builds anteriores
        try:
            # Tenta alguns patches comuns para este build
            for patch_try in [99, 98, 97, 96, 95]:  # Patches comuns
                specific_version = f"{major}.{minor}.{build_try}.{patch_try}"
                url = f"https://storage.googleapis.com/chrome-for-testing-public/{specific_version}/win32/chromedriver-win32.zip"
                response = requests.head(url, timeout=10)
                if response.status_code == 200:
                    print(f"SUCESSO: ChromeDriver encontrado para build anterior: {specific_version}")
                    return specific_version
        except Exception:
            continue
    
    # 4. Se não encontrar, tenta versões major anteriores
    for version_to_try in range(major - 1, major - 5, -1):  # Tenta até 5 versões major anteriores
        try:
            url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version_to_try}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                chromedriver_version = response.text.strip()
                print(f"SUCESSO: ChromeDriver encontrado: versão {chromedriver_version} (para Chrome {version_to_try})")
                return chromedriver_version
        except Exception as e:
            print(f"ERRO: Tentativa para versão major {version_to_try} falhou: {e}")
            continue
    
    print(f"ERRO: Não foi possível encontrar ChromeDriver compatível para Chrome {chrome_version}")
    return None

def download_chromedriver(version, download_path):
    """Faz download do ChromeDriver compatível"""
    try:
        # Determina a plataforma
        if platform.system() == "Windows":
            platform_name = "win32"
            exe_name = "chromedriver.exe"
        elif platform.system() == "Darwin":  # macOS
            platform_name = "mac64"
            exe_name = "chromedriver"
        else:  # Linux
            platform_name = "linux64"
            exe_name = "chromedriver"
        
        # Verifica se é uma versão específica (ex: 137.0.7151.68) ou versão do ChromeDriver (ex: 137.0.7151.0)
        if len(version.split('.')) == 4:  # Versão específica do Chrome for Testing
            # URL do Chrome for Testing
            url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{platform_name}/chromedriver-{platform_name}.zip"
        else:  # Versão do ChromeDriver tradicional
            # URL do download tradicional
            url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{platform_name}.zip"
        
        print(f"Baixando ChromeDriver {version} para {platform_name}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Salva o arquivo ZIP
        zip_path = download_path / "chromedriver.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extrai o ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_path)
        
        # Remove o ZIP
        zip_path.unlink()
        
        # Se for Chrome for Testing, move o executável para o diretório principal
        if len(version.split('.')) == 4:
            import shutil
            subdir = download_path / f"chromedriver-{platform_name}"
            exe_path = subdir / exe_name
            if exe_path.exists():
                dest_path = download_path / exe_name
                shutil.move(str(exe_path), str(dest_path))
                # Remove a subpasta vazia
                try:
                    subdir.rmdir()
                except Exception:
                    pass
        
        # Define permissões de execução (Linux/macOS)
        if platform.system() != "Windows":
            chromedriver_path = download_path / exe_name
            chromedriver_path.chmod(0o755)
        
        print(f"ChromeDriver {version} baixado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao baixar ChromeDriver: {e}")
        return False

def get_chromedriver_path():
    """Obtém o caminho do ChromeDriver, baixando automaticamente se necessário"""
    # Pasta para armazenar o ChromeDriver
    download_path = Path("D:/Documentos/Workspace/chromedriver")
    download_path.mkdir(exist_ok=True)
    
    # Caminho do executável
    if platform.system() == "Windows":
        chromedriver_exe = download_path / "chromedriver.exe"
    else:
        chromedriver_exe = download_path / "chromedriver"
    
    # Se já existe, retorna o caminho (sem testar)
    if chromedriver_exe.exists():
        print(f"ChromeDriver encontrado: {chromedriver_exe}")
        return str(chromedriver_exe)
    
    # Se não existe, baixa automaticamente
    print("ChromeDriver não encontrado. Baixando automaticamente...")
    
    # Obtém versão do Chrome
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("Não foi possível detectar a versão do Chrome. Verifique se o Chrome está instalado.")
        return None
    
    print(f"Versão do Chrome detectada: {chrome_version}")
    
    # Obtém versão compatível do ChromeDriver
    chromedriver_version = get_chromedriver_version_improved(chrome_version)
    if not chromedriver_version:
        print("Não foi possível obter a versão compatível do ChromeDriver.")
        print("Tentando usar webdriver-manager como fallback...")
        return "webdriver-manager"  # Indica para usar webdriver-manager
    
    print(f"Versão do ChromeDriver necessária: {chromedriver_version}")
    
    # Faz download
    if download_chromedriver(chromedriver_version, download_path):
        return str(chromedriver_exe)
    
    return None

def test_link(link: str) -> tuple[str, bool]:
    """
    Abre uma instância headless do Chrome, carrega a página
    e retorna (link, True) se estiver OK, ou (link, False) caso contrário.
    """
    # Obtém o ChromeDriver automaticamente
    chromedriver_path = get_chromedriver_path()
    if not chromedriver_path:
        print("Erro: Não foi possível obter o ChromeDriver")
        return link, False
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        if chromedriver_path == "webdriver-manager":
            # Usa webdriver-manager como fallback
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                print("Usando webdriver-manager para gerenciar o ChromeDriver")
            except ImportError:
                print("webdriver-manager não está instalado. Execute: pip install webdriver-manager")
                return link, False
        else:
            # Usa ChromeDriver baixado manualmente
            service = Service(chromedriver_path)
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.get(link)
            time.sleep(3)  # carrega JS

            src = driver.page_source.lower()
            final_url = driver.current_url.lower().rstrip("/")
            original_url = link.lower().rstrip("/")

            # 1️⃣ regra geral p/ litoraldasorte
            if "litoraldasorte.com" in original_url:
                # se houve redirecionamento para /404 OU
                # se o HTML contém "página não encontrada" OU
                # se a página está vazia ou muito pequena OU
                # se contém indicadores de erro
                if ("/404" in final_url[len("https://litoraldasorte.com"):]) or \
                   ("página não encontrada" in src) or \
                   (len(src) < 1000) or \
                   ("erro" in src and len(src) < 5000) or \
                   ("not found" in src) or \
                   ("campanha não encontrada" in src):
                    return link, False
                return link, True

            # 2️⃣ exemplo para rifasrapidas
            if "rifasrapidas.com" in original_url:
                return link, final_url == original_url

            # 3️⃣ fallback genérico
            if "404" in src or "página não encontrada" in src:
                return link, False
            return link, True

        except Exception:
            return link, False
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Erro ao inicializar ChromeDriver: {e}")
        return link, False

def main():
    print("=== Script de Verificação de Links ===")
    print("Iniciando verificação automática do ChromeDriver...")
    
    # 1) Conectar ao banco e buscar todos os links pendentes
    conn = mysql.connector.connect(
        host="pma.megatrends.site",
        user="root",
        password="Define@4536#8521",
        database="litoral"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT sigla_oficial, edicao, link
          FROM extracoes_cadastro
         WHERE status_link IN ('pendente', 'error')
    """)
    rows = cur.fetchall()
    cur.close()

    if not rows:
        print("Nenhum link pendente encontrado.")
        conn.close()
        return

    print(f"Encontrados {len(rows)} links pendentes para verificar.")

    # 2) Detectar ChromeDriver uma única vez
    print("Verificando ChromeDriver...")
    chromedriver_path = get_chromedriver_path()
    if not chromedriver_path:
        print("Erro: Não foi possível obter o ChromeDriver")
        conn.close()
        return
    
    print("ChromeDriver configurado com sucesso!")

    # prepara lista de tuplas (sigla, edicao, link)
    to_test = [(sigla, ed, link) for sigla, ed, link in rows]

    # 3) Testar em paralelo
    results = []
    with ThreadPoolExecutor(max_workers=min(len(to_test), 5)) as pool:  # Máximo 5 threads para não sobrecarregar
        futures = { pool.submit(test_link_with_driver, link, chromedriver_path): (sigla, ed, link)
                    for sigla, ed, link in to_test }
        for fut in as_completed(futures):
            sigla, ed, link = futures[fut]
            ok = False
            try:
                _, ok = fut.result()
            except Exception:
                ok = False
            results.append((sigla, ed, link, ok))

    # 4) Atualizar status no banco
    cur = conn.cursor()
    for sigla, ed, link, ok in results:
        if ok:
            cur.execute(
                "UPDATE extracoes_cadastro SET status_link='ok', status_cadastro='cadastrado', error_msg=NULL WHERE sigla_oficial=%s AND edicao=%s",
                (sigla, ed)
            )
        else:
            cur.execute(
                "UPDATE extracoes_cadastro SET status_link='error', status_cadastro='error', error_msg='link inválido' WHERE sigla_oficial=%s AND edicao=%s",
                (sigla, ed)
            )
    conn.commit()
    cur.close()
    conn.close()

    # 5) Resumo
    total = len(results)
    ok_count = sum(1 for *_, ok in results if ok)
    err_count = total - ok_count
    print(f"\nTotal testado: {total}")
    print(f"Links OK:      {ok_count}")
    print(f"Links ERRO:    {err_count}")
    if err_count:
        print("\nDetalhes dos erros:")
        for sigla, ed, link, ok in results:
            if not ok:
                print(f"  • {sigla} Edição {ed}: {link}")

def test_link_with_driver(link: str, chromedriver_path: str) -> tuple[str, bool]:
    """
    Versão otimizada que recebe o ChromeDriver já configurado
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--disable-css")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    try:
        if chromedriver_path == "webdriver-manager":
            # Usa webdriver-manager como fallback
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
            except ImportError:
                print("webdriver-manager não está instalado. Execute: pip install webdriver-manager")
                return link, False
        else:
            # Usa ChromeDriver baixado manualmente
            service = Service(chromedriver_path)
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.get(link)
            time.sleep(3)  # carrega JS

            src = driver.page_source.lower()
            final_url = driver.current_url.lower().rstrip("/")
            original_url = link.lower().rstrip("/")

            # 1️⃣ regra geral p/ litoraldasorte
            if "litoraldasorte.com" in original_url:
                # se houve redirecionamento para /404 OU
                # se o HTML contém "página não encontrada" OU
                # se a página está vazia ou muito pequena OU
                # se contém indicadores de erro
                if ("/404" in final_url[len("https://litoraldasorte.com"):]) or \
                   ("página não encontrada" in src) or \
                   (len(src) < 1000) or \
                   ("erro" in src and len(src) < 5000) or \
                   ("not found" in src) or \
                   ("campanha não encontrada" in src):
                    return link, False
                return link, True

            # 2️⃣ exemplo para rifasrapidas
            if "rifasrapidas.com" in original_url:
                return link, final_url == original_url

            # 3️⃣ fallback genérico
            if "404" in src or "página não encontrada" in src:
                return link, False
            return link, True

        except Exception:
            return link, False
        finally:
            driver.quit()
            
    except Exception as e:
        # Se falhar com o driver existente, tenta baixar uma nova versão
        print(f"Erro com ChromeDriver existente: {e}")
        print("Tentando baixar nova versão...")
        
        # Remove o driver problemático
        try:
            if chromedriver_path != "webdriver-manager":
                Path(chromedriver_path).unlink(missing_ok=True)
        except Exception:
            pass
        
        # Tenta baixar nova versão
        new_chromedriver_path = get_chromedriver_path()
        if new_chromedriver_path and new_chromedriver_path != chromedriver_path:
            print("Nova versão baixada. Tentando novamente...")
            return test_link_with_driver(link, new_chromedriver_path)
        
        return link, False

if __name__ == "__main__":
    main()
