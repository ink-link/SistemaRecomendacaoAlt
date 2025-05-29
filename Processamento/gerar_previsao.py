import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from config import MERCADOS  # Lista ordenada de mercados conforme índice


def recomendar_para_novo_usuario(matriz_utilidade: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Gera recomendações para o novo usuário com base em similaridade de usuários.

    A função assume que a última linha da matriz de utilidade representa um novo usuário,
    contendo notas de avaliação (ou zero para itens não avaliados).
    Utiliza similaridade do cosseno para prever notas não avaliadas com base nos usuários existentes.

    Parâmetros:
    -----------
    matriz_utilidade : pd.DataFrame
        DataFrame sem labels, com linhas representando usuários e colunas representando mercados (itens).
        A última linha deve ser a do novo usuário.
    top_n : int
        Número de recomendações a retornar com maiores notas previstas.

    Retorno:
    --------
    pd.DataFrame
        DataFrame contendo:
        - item_index : índice do item (coluna da matriz original)
        - nota_atual : nota do novo usuário (0 se não avaliado)
        - nota_prevista : nota estimada pelo sistema de recomendação
        - nome_mercado : nome do mercado correspondente ao índice, segundo config.MERCADOS
    """
    # Cópia da matriz original para evitar mutações acidentais
    mat = matriz_utilidade.copy()

    # Garante que os nomes das colunas são do tipo inteiro (compatível com índice em MERCADOS)
    mat.columns = mat.columns.astype(int)

    # Número de usuários (linhas) e itens (colunas)
    n_users, n_items = mat.shape

    # Separa o vetor do novo usuário (última linha)
    vetor_novo = mat.iloc[-1:].to_numpy()  # shape: (1, n_items)

    # Base de usuários existentes (todas as linhas exceto a última)
    base_usuarios = mat.iloc[:-1].to_numpy()  # shape: (n_users - 1, n_items)

    # Calcula similaridades do novo usuário com todos os usuários existentes
    similaridades = cosine_similarity(vetor_novo, base_usuarios)[0]  # shape: (n_users - 1,)

    # Inicializa vetor de predições com as notas atuais do novo usuário
    predicoes = vetor_novo.flatten().copy()  # shape: (n_items,)

    # Para cada item não avaliado (nota 0), realiza a previsão com média ponderada
    for j in range(n_items):
        if predicoes[j] == 0:
            avaliacoes = base_usuarios[:, j]     # notas dos outros usuários para o item j
            mask = avaliacoes > 0                # seleciona usuários que avaliaram esse item
            if mask.sum() > 0 and similaridades[mask].sum() > 0:
                # Previsão via média ponderada pelas similaridades
                predicoes[j] = np.dot(similaridades[mask], avaliacoes[mask]) / similaridades[mask].sum()
            else:
                predicoes[j] = 0.0  # Sem dados suficientes para prever

    # Cria DataFrame com os resultados
    df_recs = pd.DataFrame({
        'item_index': mat.columns,
        'nota_atual': vetor_novo.flatten(),
        'nota_prevista': predicoes
    })

    # Ordena pela nota prevista (decrescente) e retorna os top_n itens
    df_recs = df_recs.sort_values('nota_prevista', ascending=False).head(top_n).reset_index(drop=True)

    # Mapeia os índices dos itens para os nomes reais dos mercados
    df_recs['nome_mercado'] = df_recs['item_index'].apply(lambda i: MERCADOS[i])

    return df_recs
