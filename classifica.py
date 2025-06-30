import pandas as pd
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações
CSV_PATH = "produtos_potenciais.csv"
SELETOR_PRECO_INTEIRO = ".a-price-whole"
SELETOR_PRECO_DECIMAL = ".a-price-fraction"
SELETOR_INFORMACOES = "#rich_product_information"
TIMEOUT = 15

# Data de hoje no formato dd/mm/yyyy
data_hoje = datetime.datetime.now().strftime("%d/%m/%Y")

# Lê o CSV
df = pd.read_csv(CSV_PATH, dtype=str)
df['paginas'] = df['paginas'].astype(str)
df['ultima_avaliacao'] = df['ultima_avaliacao'].astype(str)

# Configura o Selenium (modo headless)
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

for idx, row in df.iterrows():
    precisa_atualizar = (
        row['paginas'].lower() == "false"
        or row['ultima_avaliacao'] != data_hoje
    )
    if not precisa_atualizar:
        continue

    url = row['url']
    print(f"Acessando: {url}")
    try:
        driver.get(url)
        wait = WebDriverWait(driver, TIMEOUT)

        # --- Extrai preço ---
        try:
            preco_inteiro = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELETOR_PRECO_INTEIRO))).get_attribute('textContent').strip()
            preco_decimal = driver.find_element(By.CSS_SELECTOR, SELETOR_PRECO_DECIMAL).get_attribute('textContent').strip()
            preco_str = preco_inteiro.replace('.', '').replace(',', '') + "." + preco_decimal
            preco_float = float(preco_str)
            df.at[idx, 'preco'] = preco_float
        except Exception as e:
            print(f"Preço não encontrado: {e}")
            df.at[idx, 'preco'] = ""

        # --- Extrai número de páginas via regex no texto do elemento #rich_product_information ---
        try:
            elemento_info = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELETOR_INFORMACOES)))
            texto_info = elemento_info.get_attribute('textContent')
            print('aplicando regex em: ', texto_info)
            match = re.search(r'(\d+)\s*páginas', texto_info, re.IGNORECASE)
            if match:
                paginas = match.group(1)
                df.at[idx, 'paginas'] = paginas
            else:
                print("Número de páginas não encontrado no texto do elemento.")
                df.at[idx, 'paginas'] = ""
        except Exception as e:
            print(f"Elemento #rich_product_information não encontrado: {e}")
            df.at[idx, 'paginas'] = ""

        # Atualiza a data da última avaliação
        df.at[idx, 'ultima_avaliacao'] = data_hoje

        # Salva o CSV imediatamente após processar cada linha
        df.to_csv(CSV_PATH, index=False, encoding="utf-8")
        print(f"Atualização salva para linha {idx}")

    except Exception as e:
        print(f"Erro ao processar {url}: {e}")

driver.quit()
print("Processamento finalizado!")
