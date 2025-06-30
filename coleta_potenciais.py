import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os

#configurações
URL_INICIAL = 'https://www.amazon.com.br/s?i=stripbooks&rh=n%3A7842710011%2Cp_85%3A19171728011&s=review-rank&dc&ds=v1%3AsAuvqDKVN7HWzNbc37w0Eq%2FXuczHX2F1OZ1KifHQZFg'

SELETOR_AVALIACAO = '.a-popover-trigger.a-declarative'
SELETOR_NUMERO_AVALIACOES = '[aria-label$="classificações"]'
SELETOR_CARD_PRODUTO = ".puisg-row .a-section.a-spacing-small"
SELETOR_PROXIMA_PAGINA = '.s-pagination-next'
SELETOR_PRECO_INTEIRO = '.a-price-whole'
SELETOR_PRECO_DECIMAL = '.a-price-fraction'

finalizar = False
continuar_paginacao = True

driver = webdriver.Chrome()
driver.get(URL_INICIAL)
wait = WebDriverWait(driver, 10)

def salvar_produtos_csv(lista_produtos, nome_arquivo_csv):
    fieldnames = ['nome', 'preco', 'avaliacao', 'total_avaliacoes', 'url', 'paginas', 'ultima_avaliacao']
    
    nomes_existentes = set()
    
    try:
        if os.path.exists(nome_arquivo_csv):
            with open(nome_arquivo_csv, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'nome' in row:
                        nomes_existentes.add(row['nome'])
    except IOError as e:
        print(f"Erro ao ler o arquivo existente: {e}")
        return

    try:
        with open(nome_arquivo_csv, 'a+', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            f.seek(0) 
            if f.read(1) == '':
                writer.writeheader()

            produtos_adicionados = 0
            for produto in lista_produtos:
                if produto['nome'] not in nomes_existentes:
                    writer.writerow(produto)
                    nomes_existentes.add(produto['nome'])
                    produtos_adicionados += 1
                else:
                    print(f"Produto '{produto['nome']}' já existe. Pulando.")
            
            if produtos_adicionados > 0:
                print(f"\n{produtos_adicionados} novo(s) produto(s) adicionado(s) ao arquivo '{nome_arquivo_csv}'.")
            else:
                print("\nNenhum produto novo para adicionar.")

    except IOError as e:
        print(f"Erro ao escrever no arquivo CSV: {e}")

def extrair_total_avaliacoes_do_produto(produto):
    try:
        elemento_avaliacoes = produto.find_element(By.CSS_SELECTOR, SELETOR_NUMERO_AVALIACOES)     
        string_avaliacoes_cru = elemento_avaliacoes.get_attribute('aria-label')
        string_avaliacoes_numero_com_ponto = string_avaliacoes_cru.replace(' classificações', '')
        string_avaliacoes_numero_sem_ponto = string_avaliacoes_numero_com_ponto.replace('.', '')

        total_avaliacoes = int(string_avaliacoes_numero_sem_ponto)
        return total_avaliacoes
    except Exception as e:
        salva_evidencias()
        print("Exception na função extrarir_preco_produto:", e)
        return False

def salva_evidencias():
    driver.save_screenshot("print_pagina.png")
    html = driver.page_source
    with open("pagina_salva.html", "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

def extrair_float_avaliacao_do_produto(produto):
    try:
        elemento_avaliacao_estrelas = produto.find_element(By.CSS_SELECTOR, SELETOR_AVALIACAO)
            
        string_avaliacao_estrelas_cru = elemento_avaliacao_estrelas.get_attribute("aria-label")
        
        match = re.search(r'(\d+)[,.](\d+)', string_avaliacao_estrelas_cru)
        if match:
            numero_str = match.group(0).replace(',', '.')
            return float(numero_str)
    except Exception as e:
        salva_evidencias()
        print("Exception na função extrarir_preco_produto:", e)
        return False

def extrarir_preco_produto(produto):
    try:
        preco_inteiro = produto.find_element(By.CSS_SELECTOR, SELETOR_PRECO_INTEIRO).get_attribute('textContent')
        preco_decimal = produto.find_element(By.CSS_SELECTOR, SELETOR_PRECO_DECIMAL).get_attribute('textContent')
        string_preco_com_ponto = preco_inteiro + preco_decimal
        return float(string_preco_com_ponto.replace(',', '.'))
    except Exception as e:
        salva_evidencias()
        print("Exception na função extrarir_preco_produto:", e)
        return False
try:       
    while continuar_paginacao and not finalizar:
        produtos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELETOR_CARD_PRODUTO)))
        for produto in produtos:
            preco = extrarir_preco_produto(produto)
            if (not preco): continue
            total_avaliacoes = extrair_total_avaliacoes_do_produto(produto)
            if (not total_avaliacoes): continue
            avaliacao_estrelas = extrair_float_avaliacao_do_produto(produto)
            if (not avaliacao_estrelas): continue
            nome = produto.find_element(By.CSS_SELECTOR, 'h2').get_attribute('textContent')
            url = produto.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

            if (total_avaliacoes < 100): continue
            if (re.search(r"(parte [1-9]|: [0-9]{1,2}|: ()|vol\.|volume -|volume: |volume \d|edição \d|livro \d| - .*\d\d)| [1-9]{1,2}[ $]| [0-9]{1,2}$", nome, re.IGNORECASE)): continue
            if (avaliacao_estrelas < 4.5): 
                print('avaliações baixas a partir daqui')
                finalizar = True
                continue
            
            json_produto = { 'preco': preco, 'nome': nome, 'avaliacao': avaliacao_estrelas, 'total_avaliacoes': total_avaliacoes, 'url': url, 'paginas': False, 'ultima_avaliacao': False  }
            
            salvar_produtos_csv([json_produto], 'produtos_potenciais.csv')
            
        elemento_proxima_pagina = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELETOR_PROXIMA_PAGINA)))
        
        if (elemento_proxima_pagina):
            elemento_proxima_pagina.click()
        else:
            print('Não encontrou botão continuar')
            continuar_paginacao = False
    
except:
    print('UAIIIIII')
    salva_evidencias()
    raise

driver.quit()