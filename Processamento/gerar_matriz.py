import numpy as np
import pandas as pd
from config import ITENS_DISPONIVEIS, SAZONALIDADE, MERCADOS


def gerar_matriz_usuario_item(mes=5, percentual_organico=0.3, num_usuarios=5000):
    """
    Gera a matriz de preferência de usuários por itens sazonais.

    Parâmetros
    ----------
    mes : int
        Mês atual para filtrar itens sazonais.
    percentual_organico : float
        Proporção de usuários com preferência por produtos orgânicos (0 a 1).
    num_usuarios : int
        Número total de usuários simulados.

    Saída
    -----
    Salva o arquivo 'usuario_item.csv' contendo:
        - Pesos de interesse por item sazonal (linha: usuário, coluna: item).
        - Coluna 'Organico' indicando se o usuário tem preferência orgânica.
    """
    np.random.seed(42)

    # Filtra itens disponíveis para o mês atual
    itens_sazonais = [
        item for item in ITENS_DISPONIVEIS if mes in SAZONALIDADE.get(item, [])
    ]
    num_itens = len(itens_sazonais)

    # Inicializa matriz de zeros (usuários x itens)
    matriz_usuario_item = np.zeros((num_usuarios, num_itens))

    # Atribui pesos aleatórios para os itens escolhidos por cada usuário
    for usuario_id in range(num_usuarios):
        n = np.random.randint(1, num_itens)
        itens_escolhidos = np.random.choice(range(num_itens), n, replace=False)
        for item_id in itens_escolhidos:
            matriz_usuario_item[usuario_id, item_id] = 1 / n  # Peso igual por item

    usuario_item = pd.DataFrame(matriz_usuario_item, columns=itens_sazonais)

    # Define usuários com preferência por orgânicos
    qtd_organicos = int(num_usuarios * percentual_organico)
    organico = np.array([1] * qtd_organicos + [0] * (num_usuarios - qtd_organicos))
    np.random.shuffle(organico)
    usuario_item["Organico"] = organico

    usuario_item = usuario_item.round(2)
    usuario_item.to_csv("usuario_item.csv", index=False)

    print("Matriz de usuário x item salva com sucesso.")


def gerar_matriz_item_mercado(mes):
    """
    Gera a matriz de disponibilidade de itens sazonais por mercado.

    Parâmetros
    ----------
    mes : int
        Mês atual para filtrar itens sazonais.

    Saída
    -----
    Salva o arquivo 'item_mercado.csv' contendo:
        - Disponibilidade de itens por mercado.
        - Linha 'Organico' indicando se o mercado oferece produtos orgânicos.
    """
    np.random.seed(42)

    # Filtra itens sazonais
    itens_sazonais = [
        item for item in ITENS_DISPONIVEIS if mes in SAZONALIDADE.get(item, [])
    ]
    num_itens = len(itens_sazonais)
    num_mercados = len(MERCADOS)

    # Cria matriz de disponibilidade aleatória
    matriz_item_mercado = np.random.rand(num_itens, num_mercados)
    item_mercado = pd.DataFrame(matriz_item_mercado, index=itens_sazonais, columns=MERCADOS)

    # Alterna oferta orgânica por cidade
    contagem = {}
    org_flag = []
    for mercado in MERCADOS:
        cidade = mercado.rsplit("  ", 1)[-1]
        contagem[cidade] = contagem.get(cidade, 0) + 1
        org_flag.append(1 if contagem[cidade] % 2 == 1 else 0)

    # Adiciona linha 'Organico' com flag por mercado
    item_mercado.loc["Organico"] = org_flag
    item_mercado = item_mercado.round(2)
    item_mercado.to_csv("item_mercado.csv", index=True)

    print("Matriz item x mercado salva com sucesso.")


def gerar_matriz_utilidade(
    path_usuario_item="usuario_item.csv",
    path_item_mercado="item_mercado.csv",
    path_saida="matriz_utilidade.csv"
):
    """
    Gera a matriz de utilidade combinando usuários, itens e mercados.

    Penaliza usuários com preferência por orgânicos em mercados não-orgânicos.

    Parâmetros
    ----------
    path_usuario_item : str
        Caminho para o CSV contendo a matriz usuário x item.
    path_item_mercado : str
        Caminho para o CSV contendo a matriz item x mercado.
    path_saida : str
        Caminho para salvar a matriz final de utilidade (usuário x mercado).

    Saída
    -----
    Salva o arquivo 'matriz_utilidade.csv' com os pesos de utilidade por usuário e mercado.
    """
    user_item = pd.read_csv(path_usuario_item, header=None).iloc[1:].reset_index(drop=True)
    item_mercado = pd.read_csv(path_item_mercado, header=None).iloc[1:, 1:].reset_index(drop=True)

    usuario_organico = user_item.iloc[:, -1].astype(float)
    mercado_organico = item_mercado.iloc[-1, :].astype(float)

    usuario_item_sem_org = user_item.iloc[:, :-1].astype(float)
    item_mercado_sem_org = item_mercado.iloc[:-1, :].astype(float)

    # Produto matricial: (usuários x itens) x (itens x mercados)
    matriz_utilidade = usuario_item_sem_org @ item_mercado_sem_org

    # Penaliza mercados não-orgânicos para usuários orgânicos
    for user_idx in matriz_utilidade.index:
        for mercado_idx in matriz_utilidade.columns:
            if usuario_organico[user_idx] == 1.0 and mercado_organico[mercado_idx] == 0.0:
                matriz_utilidade.loc[user_idx, mercado_idx] *= 0.6

    matriz_utilidade.to_csv(path_saida, index=False)
    print("Matriz de utilidade salva com sucesso.")


def calcular_utilidade_novo_usuario(
    itens_preferidos,
    organico,
    mes,
    path_item_mercado="item_mercado.csv"
):
    """
    Calcula a utilidade de um novo usuário com base em itens preferidos e preferência por produtos orgânicos.

    Parâmetros
    ----------
    itens_preferidos : list of str
        Lista de nomes de itens que o usuário prefere.
    organico : int
        1 se o usuário prefere produtos orgânicos, 0 caso contrário.
    mes : int
        Mês atual (para considerar sazonalidade).
    path_item_mercado : str
        Caminho para a matriz de item x mercado.

    Retorno
    -------
    pandas.Series
        Série com valores de utilidade do usuário para cada mercado.
    """
    item_mercado = pd.read_csv(path_item_mercado, index_col=0)

    mercado_organico = item_mercado.loc["Organico"]
    item_mercado_sem_org = item_mercado.drop(index="Organico")

    # Filtra itens válidos (sazonais e existentes na matriz)
    itens_validos = [
        item for item in itens_preferidos
        if mes in SAZONALIDADE.get(item, []) and item in item_mercado_sem_org.index
    ]

    if not itens_validos:
        raise ValueError("Nenhum item preferido está disponível neste mês ou presente na matriz.")

    # Peso igual para todos os itens preferidos
    pesos = np.array([1 / len(itens_validos)] * len(itens_validos))

    vetor_usuario = pd.Series(0, index=item_mercado_sem_org.index, dtype=float)
    vetor_usuario.loc[itens_validos] = pesos

    utilidade = vetor_usuario @ item_mercado_sem_org

    # Penaliza mercados que não oferecem produtos orgânicos
    if organico == 1:
        utilidade = utilidade.where(mercado_organico == 1, utilidade * 0.6)

    return utilidade.round(2)
