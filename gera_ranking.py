import csv

# Nome do arquivo CSV de entrada e TXT de saída
input_csv = 'produtos_potenciais.csv'
output_txt = 'produtos_ordenados.txt'

# Lista para armazenar os produtos com custo por página calculado
produtos = []

# Abrir e ler o CSV
with open(input_csv, newline='', encoding='utf-8') as csvfile:
    leitor = csv.DictReader(csvfile)
    for linha in leitor:
        # Converter os campos numéricos para float ou int conforme necessário
        preco = float(linha['preco'])
        paginas = int(linha['paginas'])
        
        # Calcular custo por página
        custo_por_pagina = preco / paginas if paginas > 0 else float('inf')
        
        # Adicionar o produto com o custo calculado
        produto = {
            'nome': linha['nome'],
            'preco': preco,
            'avaliacao': linha['avaliacao'],
            'total_avaliacoes': linha['total_avaliacoes'],
            'url': linha['url'],
            'paginas': paginas,
            'ultima_avaliacao': linha['ultima_avaliacao'],
            'custo_por_pagina': custo_por_pagina
        }
        produtos.append(produto)

# Ordenar a lista pelo custo por página (menor para maior)
produtos.sort(key=lambda x: x['custo_por_pagina'])

# Escrever o resultado no arquivo TXT formatado
with open(output_txt, 'w', encoding='utf-8') as f:
    for p in produtos:
        f.write(f"Nome: {p['nome']}\n")
        f.write(f"Preço: R$ {p['preco']:.2f}\n")
        f.write(f"Avaliação: {p['avaliacao']} ({p['total_avaliacoes']} avaliações)\n")
        f.write(f"URL: {p['url']}\n")
        f.write(f"Páginas: {p['paginas']}\n")
        f.write(f"Última Avaliação: {p['ultima_avaliacao']}\n")
        f.write(f"Custo por Página: R$ {p['custo_por_pagina']:.4f}\n")
        f.write("\n")  # Parágrafo entre produtos
