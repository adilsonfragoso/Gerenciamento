from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import unidecode
import os
import pandas as pd
import pdfkit
import sys
import subprocess
from selenium.common.exceptions import TimeoutException

print("Python executado:", sys.executable)

# -------------------- PARÂMETRO --------------------
edicao_converter = sys.argv[1]
print(f"EDICAO SOLICITADA: {edicao_converter}")
print("INICIANDO PROCESSAMENTO...")

# -------------------- SELENIUM ---------------------
HEADLESS = True
driver_path = r"D:\Documentos\Workspace\chromedriver.exe"
service = Service(driver_path)

if HEADLESS:
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_opts.add_experimental_option("useAutomationExtension", False)
    navegador = webdriver.Chrome(service=service, options=chrome_opts)
else:
    navegador = webdriver.Chrome(service=service)

caminho_downloads = r"D:\Adilson\Downloads"

# -------------------- LOGIN ------------------------
print("CONECTANDO AO PAINEL...")
navegador.get("https://painel.litoraldasorte.com")
sleep(2)
navegador.execute_script("window.print = function(){};")

print("FAZENDO LOGIN...")
navegador.find_element(By.NAME, "email").send_keys("relatorio")
navegador.find_element(By.NAME, "password").send_keys("Define@4536#8521")
navegador.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
sleep(4)

def fechar_popup():
    try:
        btn = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Entendi']"))
        )
        btn.click()
        WebDriverWait(navegador, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.MuiDialog-container"))
        )
        print("Pop-up fechado.")
    except TimeoutException:
        print("Pop-up não apareceu.")

fechar_popup()
sleep(2)

# -------------------- MENU / DOWNLOAD --------------
navegador.find_element(
    By.XPATH,
    '//*[@id="root"]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div[2]/ul[1]/div[2]/div[2]/span',
).click()
sleep(6)

print(f"BUSCANDO EDICAO {edicao_converter}...")
busca = navegador.find_element(By.XPATH, "//input[@placeholder='Pesquisar por título do sorteio...']")
busca.clear(); busca.send_keys(edicao_converter)
sleep(5)

print("ACESSANDO RELATORIOS...")
navegador.find_element(By.XPATH, "//button[@aria-label='Compras']").click()
sleep(3)

ac = ActionChains(navegador)
for _ in range(6): ac.send_keys(Keys.TAB).pause(0.5)
ac.send_keys(Keys.ENTER).perform()
sleep(3)

try:
    WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li//div[contains(text(), 'Relatório de Vendas')]"))
    ).click()
    print("GERANDO RELATORIO DE VENDAS...")
    sleep(2)
except Exception as e:
    print(f"Erro ao selecionar relatório: {e}")

titulo = navegador.find_element(
    By.XPATH,
    '//*[@id="root"]/div/main/div/div/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div[1]/div/div[1]/div/h4',
).text
nome_csv = f"relatorio-vendas-{unidecode.unidecode(titulo.lower().replace(' ', '-'))}.csv"
caminho_csv = os.path.join(caminho_downloads, nome_csv)

for i in range(10):
    if os.path.exists(caminho_csv):
        print("CSV baixado.")
        break
    sleep(1)
else:
    print("CSV não encontrado."); navegador.quit(); sys.exit(1)

# -------------------- PDF CONFIG -------------------
wkhtml = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config_pdf = pdfkit.configuration(wkhtmltopdf=wkhtml)

def criptografar(tel):
    return tel[:7] + "***-**" + tel[-2:] if len(tel) == 15 else tel

# -------------------- PROCESSAMENTO ----------------
print("PROCESSANDO DADOS...")
df = pd.read_csv(caminho_csv, sep=";", encoding="utf-8")
df = df.iloc[:, [6, 7, 20]]          # Nome, Telefone, Números adquiridos
df.columns = ["Nome", "Telefone", "Números"]

def juntar(series):
    nums = []
    for item in series:
        nums += [p.strip() for p in str(item).split(",") if p.strip()]
    nums = sorted(set(nums), key=int)
    return ", ".join(nums)

agrupado = (
    df.groupby("Telefone")
      .agg(Nome=("Nome", "first"), Números=("Números", juntar))
      .reset_index()
)

agrupado["Telefone"] = agrupado["Telefone"].apply(criptografar)
agrupado = agrupado[["Nome", "Telefone", "Números"]]
agrupado = agrupado.sort_values("Nome")

# -------------------- GERAR HTML/PDF ----------------
print("CRIANDO PDF...")
html = f"""
<html><head><meta charset="utf-8"><style>
 body{{font-family:Arial,sans-serif;margin:0;padding:0}}
 h1{{
     text-align:center;
     margin:25px 0 15px 0;
     font-size:24pt;
     font-weight:bold;
     color:#0d47a1;
 }}
 table{{width:100%;border-collapse:collapse}}
 colgroup {{
     width:100%;
 }}
 th,td{{border:1px solid #ddd;padding:8px}}
 th{{
     background:#6495ED;           /* cabeçalho */
     color:#fff;
     text-align:center;
     font-size:18pt;               /* +2 pt */
 }}
 td{{font-size:16pt}}              /* +1 pt */
 td:nth-child(2),th:nth-child(2){{text-align:center}}
 th:first-child,td:first-child{{width:48%;white-space:normal;word-wrap:break-word}}
 th:nth-child(2),td:nth-child(2){{width:20%}}
 th:nth-child(3),td:nth-child(3){{width:32%;text-align:center}}
 tr:nth-child(even) td{{background:#f6f6f6}}  /* zebra */
</style></head><body>
<h1>{titulo}</h1>
{agrupado.to_html(index=False, border=0)}
</body></html>
"""
tmp_html = os.path.join(caminho_downloads, "relatorio_temp.html")
with open(tmp_html, "w", encoding="utf-8") as f:
    f.write(html)

caminho_pdf = caminho_csv.replace(".csv", ".pdf")
pdfkit.from_file(tmp_html, caminho_pdf, configuration=config_pdf)
os.remove(tmp_html)
print("PDF GERADO COM SUCESSO!")

# -------------------- INSERIR NO BD ----------------
try:
    subprocess.run(
        ["python", "D:/Documentos/Workspace/inserir_no_bd.py", edicao_converter, caminho_csv],
        check=True,
    )
    print("Dados salvos no banco.")
except Exception as e:
    print(f"Falha ao salvar no banco: {e}")

if os.path.exists(caminho_csv):
    os.remove(caminho_csv)
    print("CSV temporário removido.")

# -------------------- FINAL ------------------------
navegador.quit()
print("RELATORIO CONCLUIDO!")
print(os.path.join(caminho_downloads, nome_csv.replace(".csv", ".pdf")))
