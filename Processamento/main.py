import pandas as pd
import numpy as np
import unicodedata
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic

from Processamento.config import ITENS_DISPONIVEIS, SAZONALIDADE
from Processamento.gerar_previsao import recomendar_para_novo_usuario
from Processamento.gerar_matriz import (
    gerar_matriz_usuario_item,
    gerar_matriz_item_mercado,
    gerar_matriz_utilidade,
    calcular_utilidade_novo_usuario
)

# =============================================================================
# ENTRADAS DO USUÁRIO
# =============================================================================

ENDERECO_USUARIO = "ULEG UNB"
ITENS_PREFERIDOS = ["Banana", "Manga", "Tomate"]
ORGANICO = 1  # 1 = Sim, 0 = Não
MES_ATUAL = 5
DISTANCIA = 20

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def normalize_str(s):
    s = str(s).lower().strip().replace(',', '').replace('"', '')
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s

def gerar_recomendacoes(endereco, itens_preferidos, organico, mes_atual, distancia_max_km, latitude=None, longitude=None):
    print("DEBUG:", endereco, itens_preferidos, organico, mes_atual, distancia_max_km, latitude, longitude)
    # Se latitude e longitude forem fornecidos, use-os; senão, geocode o endereço
    if latitude is not None and longitude is not None:
        user_location = (float(latitude), float(longitude))
    else:
        coordenadas = get_coordinates(endereco)
        if not coordenadas:
            return []
        user_location = coordenadas   

    try:
        df = pd.read_csv("Processamento/coordenadas_associacoes_df.csv")
        print("DataFrame de coordenadas carregado com sucesso.")
    except FileNotFoundError:
        print("[Erro] DataFrame de coordenadas está vazio.")
        return []

    df["Distance_km"] = df.apply(
        lambda row: calculate_distance(row["Latitude"], row["Longitude"], user_location),
        axis=1
    )
    df_proximas = df[df["Distance_km"] <= distancia_max_km].sort_values("Distance_km")
    print("Mercados próximos:", df_proximas)
    if df_proximas.empty:
        return []

    itens_preferidos_sazonais = [
        item for item in itens_preferidos
        if mes_atual in SAZONALIDADE.get(item, [])
    ]
    print("Itens sazonais:", itens_preferidos_sazonais)
    if not itens_preferidos_sazonais:
        return []

    # indices_proximos = df_proximas.index.tolist()
    colunas_proximas = [
        normalize_str(m) + ' ' + normalize_str(e)
        for m, e in zip(df_proximas['Mercado'], df_proximas['Endereço'])
    ]
    print("Colunas_proximas:", colunas_proximas)

    gerar_matriz_usuario_item(mes=mes_atual, percentual_organico=0.3, num_usuarios=5000)
    gerar_matriz_item_mercado(mes=mes_atual)
    gerar_matriz_utilidade()
    linha_novo_usuario = calcular_utilidade_novo_usuario(
        itens_preferidos_sazonais, organico, mes=mes_atual
    ).to_numpy()
    linha_novo_usuario = np.where(linha_novo_usuario >= 0.3, linha_novo_usuario, 0)
    try:
        matriz_utilidade = pd.read_csv("Processamento/matriz_utilidade.csv")
    except FileNotFoundError:
        return []
    matriz_utilidade.loc[len(matriz_utilidade)] = linha_novo_usuario
    matriz_utilidade.columns = [normalize_str(col) for col in matriz_utilidade.columns]
    matriz_utilidade.to_csv("Processamento/nova_matriz_utilidade.csv", index=False)
    print("Colunas normalizadas em nova_matriz_utilidade.csv:", matriz_utilidade.columns.tolist())

    matriz_utilidade_final = pd.read_csv("Processamento/nova_matriz_utilidade.csv", usecols=colunas_proximas)
    matriz_utilidade_final.to_csv("Processamento/matriz_utilidade_final.csv", index=False)
    recomendacoes = recomendar_para_novo_usuario(matriz_utilidade_final, top_n=3)
    
    print("Colunas do CSV:", matriz_utilidade.columns.tolist())
    print("Colunas_proximas:", colunas_proximas)

    df_proximas['chave'] = (df_proximas['Mercado'].str.strip() + ' ' + df_proximas['Endereço'].str.strip()).apply(normalize_str)
    recomendacoes['nome_mercado'] = recomendacoes['nome_mercado'].apply(normalize_str)

    print("Chaves em df_proximas:")
    print(df_proximas['chave'].unique())
    print("Mercados recomendados:")
    print(recomendacoes['nome_mercado'].unique())

    mercados_recomendados = []
    for idx in recomendacoes["nome_mercado"].index:
        mercado = recomendacoes.iloc[idx]
        df_mercado = df_proximas[df_proximas['chave'] == mercado['nome_mercado']]
        if not df_mercado.empty:
            info = df_mercado.iloc[0]
            mercados_recomendados.append({
                "Nome": mercado['nome_mercado'].title(),
                "Latitude": info['Latitude'],
                "Longitude": info['Longitude'],
                "Distance_km": info['Distance_km']
            })
        else:
            print(f"[AVISO] Mercado '{mercado['nome_mercado']}' não encontrado em df_proximas.")
    return mercados_recomendados

def get_coordinates(address: str) -> tuple[float, float] | None:
    """
    Obtém as coordenadas (latitude, longitude) de um endereço usando o Nominatim.

    Parâmetros:
        address (str): Endereço a ser geocodificado.

    Retorno:
        tuple[float, float] | None: Coordenadas geográficas ou None se não encontrado.
    """
    geolocator = Nominatim(user_agent="meu_app_localizacao")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        print(f"[Erro] Endereço não encontrado: {address}")
    except GeocoderTimedOut:
        print(f"[Erro] Timeout ao tentar geocodificar: {address}")
    return None


def calculate_distance(
    market_lat: float, market_lon: float, user_location: tuple[float, float]
) -> float:
    """
    Calcula a distância geodésica entre o usuário e um mercado.

    Parâmetros:
        market_lat (float): Latitude do mercado.
        market_lon (float): Longitude do mercado.
        user_location (tuple): Coordenadas do usuário (latitude, longitude).

    Retorno:
        float: Distância em quilômetros.
    """
    market_location = (market_lat, market_lon)
    return geodesic(user_location, market_location).km


# =============================================================================
# PROCESSAMENTO PRINCIPAL
# =============================================================================

def main() -> None:
    """
    Executa o pipeline completo de recomendação com base na localização do usuário,
    itens preferidos e sazonalidade.
    """
    # Obter coordenadas do usuário
    coordenadas = get_coordinates(ENDERECO_USUARIO)
    if not coordenadas:
        print("[Erro crítico] Não foi possível localizar o endereço informado.")
        return

    user_location = coordenadas

    # Carregar base de dados dos mercados
    try:
        df = pd.read_csv("Processamento/coordenadas_associacoes_df.csv")
    except FileNotFoundError:
        print("[Erro] Arquivo 'coordenadas_associacoes_df.csv' não encontrado.")
        return

    # Calcular distância entre usuário e mercados
    df["Distance_km"] = df.apply(
        lambda row: calculate_distance(row["Latitude"], row["Longitude"], user_location),
        axis=1
    )

    # Filtrar mercados em até DISTANCIA km
    df_proximas = df[df["Distance_km"] <= DISTANCIA].sort_values("Distance_km")

    if df_proximas.empty:
        print("Nenhum mercado encontrado num raio de 20 km.")
        return

    # Filtrar itens preferidos sazonais no mês atual
    itens_preferidos_sazonais = [
        item for item in ITENS_PREFERIDOS
        if MES_ATUAL in SAZONALIDADE.get(item, [])
    ]

    if not itens_preferidos_sazonais:
        print("Nenhum item preferido é sazonal no mês atual.")
        return

    # Obter os índices dos mercados próximos
    indices_proximos = df_proximas.index.tolist()

    # Geração de matrizes de recomendação
    gerar_matriz_usuario_item(mes=MES_ATUAL, percentual_organico=0.3, num_usuarios=5000)
    gerar_matriz_item_mercado(mes=MES_ATUAL)
    gerar_matriz_utilidade()

    # Calcular a linha de utilidade para o novo usuário
    linha_novo_usuario = calcular_utilidade_novo_usuario(
        itens_preferidos_sazonais, ORGANICO, mes=MES_ATUAL
    ).to_numpy()

    # Aplicar limiar mínimo de utilidade
    linha_novo_usuario = np.where(linha_novo_usuario >= 0.3, linha_novo_usuario, 0)

    # Atualizar matriz de utilidade
    try:
        matriz_utilidade = pd.read_csv("Processamento/matriz_utilidade.csv")
    except FileNotFoundError:
        print("[Erro] Arquivo 'matriz_utilidade.csv' não encontrado.")
        return

    matriz_utilidade.loc[len(matriz_utilidade)] = linha_novo_usuario
    matriz_utilidade.to_csv("Processamento/nova_matriz_utilidade.csv", index=False)

    # Manter apenas mercados próximos
    matriz_utilidade_final = pd.read_csv("Processamento/nova_matriz_utilidade.csv", usecols=indices_proximos)
    matriz_utilidade_final.to_csv("Processamento/matriz_utilidade_final.csv", index=False)

    # Gerar recomendações
    recomendacoes = recomendar_para_novo_usuario(matriz_utilidade_final, top_n=3)

    # Apresentar recomendações
    mercados_recomendados = recomendacoes["nome_mercado"].tolist()
    print("Mercados recomendados:", mercados_recomendados)
    print("Programa finalizado com sucesso.")


if __name__ == "__main__":
    main()
