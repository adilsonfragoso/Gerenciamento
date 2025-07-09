#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se o ChromeDriver está funcionando corretamente
"""

import subprocess
import requests
import zipfile
import platform
from pathlib import Path

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

def test_chromedriver():
    """Testa se o ChromeDriver está funcionando"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Pasta para armazenar o ChromeDriver
        download_path = Path("D:/Documentos/Workspace/chromedriver")
        download_path.mkdir(exist_ok=True)
        
        # Caminho do executável
        if platform.system() == "Windows":
            chromedriver_exe = download_path / "chromedriver.exe"
        else:
            chromedriver_exe = download_path / "chromedriver"
        
        # Se já existe, tenta usar diretamente
        if chromedriver_exe.exists():
            try:
                # Tenta usar o ChromeDriver existente
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                
                service = Service(str(chromedriver_exe))
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.quit()
                print(f"✅ ChromeDriver encontrado e funcionando: {chromedriver_exe}")
                return True
            except Exception as e:
                print(f"❌ ChromeDriver existente não funciona: {e}")
                # Remove o arquivo corrompido
                chromedriver_exe.unlink(missing_ok=True)
        
        # Obtém versão do Chrome
        chrome_version = get_chrome_version()
        if not chrome_version:
            print("❌ Não foi possível detectar a versão do Chrome. Verifique se o Chrome está instalado.")
            return False
        
        print(f"🔍 Versão do Chrome detectada: {chrome_version}")
        
        # Obtém versão compatível do ChromeDriver
        chromedriver_version = get_chromedriver_version_improved(chrome_version)
        if not chromedriver_version:
            print("❌ Não foi possível obter a versão compatível do ChromeDriver.")
            return False
        
        print(f"📦 Versão do ChromeDriver necessária: {chromedriver_version}")
        
        # Faz download
        if download_chromedriver(chromedriver_version, download_path):
            # Testa o ChromeDriver baixado
            try:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                
                service = Service(str(chromedriver_exe))
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.quit()
                print(f"✅ ChromeDriver {chromedriver_version} baixado e funcionando!")
                return True
            except Exception as e:
                print(f"❌ ChromeDriver baixado não funciona: {e}")
                return False
        
        return False
        
    except ImportError:
        print("❌ Selenium não está instalado. Execute: pip install selenium")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    print("=== Teste do ChromeDriver ===")
    print("Verificando se o ChromeDriver está funcionando...")
    
    if test_chromedriver():
        print("\n✅ Teste concluído com sucesso!")
        print("O ChromeDriver está funcionando corretamente.")
    else:
        print("\n❌ Teste falhou!")
        print("Verifique se:")
        print("1. O Google Chrome está instalado")
        print("2. O Selenium está instalado (pip install selenium)")
        print("3. A conexão com a internet está funcionando")

if __name__ == "__main__":
    main() 