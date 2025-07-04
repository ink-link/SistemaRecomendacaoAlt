# config.py

# Lista principal de itens
ITENS_DISPONIVEIS = [
    "Abacate", "Atemóia", "Banana", "Cajamanga", "Coco", "Goiaba", "Graviola", "Limão",
    "Lichia", "Mamão", "Manga", "Maracujá", "Morango", "Pitaia", "Tangerina", "Uva",
    "Abóbora", "Agrião", "Alface", "Batata", "Berinjela", "Beterraba", "Brócolis",
    "Cebola", "Cenoura", "Chuchu", "Couve", "Gengibre", "Jiló", "Mandioca", "Pepino",
    "Pimentão", "Quiabo", "Repolho", "Tomate"
]

# Mapeamento de sazonalidade
SAZONALIDADE = {
    "Abacate": [2,3,4],
    "Atemóia": [11,12,1,2],
    "Banana": [3,4,5,6,7,8,10,11,12],
    "Cajamanga": [12,1,2,3],
    "Coco": [1,2,3,4,5,6,7,8,9,10,11,12],
    "Goiaba": [2,3,4],
    "Graviola": [1,2,3],
    "Limão": [1,2,3,4,5,6],
    "Lichia": [12,1],
    "Mamão": [1,2,3,10,11,12],
    "Manga": [1,2,3,5,10,11,12],
    "Maracujá": [1,2,3,10,11,12],
    "Morango": [8],
    "Pitaia": [12,1,2,3,4],
    "Tangerina": [6,7,8,9],
    "Uva": [1,2,3,4,5,6,7],
    "Abóbora": [2,3,4,5,6,7,8,9,10,11],
    "Agrião": [6,7,8],
    "Alface": [1,3,4],
    "Batata": [5,6,7,8,9],
    "Berinjela": [3,5,6,10,11],
    "Beterraba": [2,3,5,6,10,11,12],
    "Brócolis": [6,8,9,10],
    "Cebola": [6,7,8,9,10],
    "Cenoura": [5,7,8,10,11,12],
    "Chuchu": [3,5,10],
    "Couve": [7,8,9],
    "Gengibre": [3,6,10],
    "Jiló": [3],
    "Mandioca": [6,9,10],
    "Pepino": [2,3,8,10],
    "Pimentão": [10,11,12],
    "Quiabo": [2,3],
    "Repolho": [2,3,4],
    "Tomate": [2,3,5,10]
}

import pandas as pd

# Carregue o CSV
df = pd.read_csv("Processamento/coordenadas_associacoes_df.csv")

# Crie a lista de chaves únicas: nome + endereço, padronizados
MERCADOS = (df['Mercado'].str.strip() + ' ' + df['Endereço'].str.strip()).tolist()

# MERCADOS = [
#     "Afeca  São Sebastião",
#     "Agrifam  Taguatinga",
#     "Agrifam  Gama",
#     "Agrifam  Santa Maria",
#     "Amista  Santa Maria",
#     "Aspaf  Guará",
#     "Aspaf  Núcleo Bandeirante",
#     "Aspaf  Plano Piloto",
#     "AsSpag  Brazlândia",
#     "Asphor  Gama",
#     "Asphor  Santa Maria",
#     "Asphor  Plano Piloto",
#     "Asproc  Ceilândia",
#     "Asproc  Recanto das Emas",
#     "Asproc  Samambaia",
#     "Asproc  Paranoá",
#     "Asproc  Planaltina",
#     "Aspronte  Ceilândia",
#     "Aspronte  Recanto das Emas",
#     "Astraf  Guará",
#     "Coopbrasfil  Gama",
#     "Coopbrasfil  Recanto das Emas",
#     "Coopbrasfil  Samambaia",
#     "Coopbrasfil  Núcleo Bandeirante",
#     "Coopbrasfil  Planaltina",
#     "Coopbrasfil  Brazlândia",
#     "Coopbrasfil  Ceilândia",
#     "Cooper-Horti  Paranoá",
#     "Prorural  Plano Piloto",
#     "Prorural  Paranoá",
#     "Coopebraz  Brazlândia",
#     "Coopebraz  Taguatinga",
#     "Coopebraz  Samambaia",
#     "Coopebraz  Recanto das Emas",
#     "Coopermista  Planaltina",
#     "Rede Terra  Santa Maria",
#     "Cootagua  Ceilândia",
#     "Cooperbrasilia  Sobradinho",
#     "Cooperbrasilia  São Sebastião"
# ]