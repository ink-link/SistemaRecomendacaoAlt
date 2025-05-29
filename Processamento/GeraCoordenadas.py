import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# =============================================================================
# LISTA DE ASSOCIAÇÕES E LOCALIDADES
# =============================================================================

enderecos = [
    # (Nome da Associação, Localização)
    ("Associação de Agricultores Familiares da Eco Comunidade do Assentamento 15 de Agosto (Afeca)", "São Sebastião, DF"),
    ("Associação Agrícola do Distrito Federal e Ride (Agrifam)", "Taguatinga, DF"),
    ("Associação Agrícola do Distrito Federal e Ride (Agrifam)", "Gama, DF"),
    ("Associação Agrícola do Distrito Federal e Ride (Agrifam)", "Santa Maria, DF"),
    ("Associação Mista dos Agricultores Familiares, Orgânicos e Produtores Rurais do DF e Entorno (Amista)", "Santa Maria, DF"),
    ("Associação dos Produtores da Agricultura Familiar (Aspaf)", "Guará, DF"),
    ("Associação dos Produtores da Agricultura Familiar (Aspaf)", "Núcleo Bandeirante, DF"),
    ("Associação dos Produtores da Agricultura Familiar (Aspaf)", "Plano Piloto, DF"),
    ("Associação dos Produtores Rurais de Alexandre Gusmão (AsSpag)", "Brazlândia, DF"),
    ("Associação dos Produtores de Hortigranjeiros do Distrito Federal (Asphor)", "Gama, DF"),
    ("Associação dos Produtores de Hortigranjeiros do Distrito Federal (Asphor)", "Santa Maria, DF"),
    ("Associação dos Produtores de Hortigranjeiros do Distrito Federal (Asphor)", "Plano Piloto, DF"),
    ("Associação dos Produtores Rurais Orgânicos e Convencionais do Distrito Federal e Entorno (Asproc)", "Ceilândia, DF"),
    ("Associação dos Produtores Rurais Orgânicos e Convencionais do Distrito Federal e Entorno (Asproc)", "Recanto das Emas, DF"),
    ("Associação dos Produtores Rurais Orgânicos e Convencionais do Distrito Federal e Entorno (Asproc)", "Samambaia, DF"),
    ("Associação dos Produtores Rurais Orgânicos e Convencionais do Distrito Federal e Entorno (Asproc)", "Paranoá, DF"),
    ("Associação dos Produtores Rurais Orgânicos e Convencionais do Distrito Federal e Entorno (Asproc)", "Planaltina, DF"),
    ("Associação dos Produtores Rurais Novo Horizonte Betinho (Aspronte)", "Ceilândia, DF"),
    ("Associação dos Produtores Rurais Novo Horizonte Betinho (Aspronte)", "Recanto das Emas, DF"),
    ("Associação dos Trabalhadores Rurais da Agricultura Familiar do Assentamento Chapadinha (Astraf)", "Guará, DF"),
    ("Cooperativa Mista da Agricultura Familiar do Meio Ambiente e da Cultura do Brasil (Coopbrasfil)", "Gama, DF"),
    ("Cooperativa Mista da Agricultura Familiar do Meio Ambiente e da Cultura do Brasil (Coopbrasfil)", "Recanto das Emas, DF"),
    ("Cooperativa Mista da Agricultura Familiar do Meio Ambiente e da Cultura do Brasil (Coopbrasfil)", "Samambaia, DF"),
    ("Cooperativa Mista da Agricultura Familiar do Meio Ambiente e da Cultura do Brasil (Coopbrasfil)", "Núcleo Bandeirante, DF"),
    ("Cooperativa Mista da Agricultura Familiar do Meio Ambiente e da Cultura do Brasil (Coopbrasfil)", "Planaltina, DF"),
    ("Cooperativa Mista da Agricultura Familiar do Meio Ambiente e da Cultura do Brasil (Coopbrasfil)", "Brazlândia, DF"),
    ("Cooperativa Mista da Agricultura Familiar do Meio Ambiente e da Cultura do Brasil (Coopbrasfil)", "Ceilândia, DF"),
    ("Cooperativa Agrícola Buriti Vermelho (Cooper-Horti)", "Paranoá, DF"),
    ("Cooperativa dos Produtores Rurais de Planaltina de Goiás e Região (Prorural)", "Plano Piloto, DF"),
    ("Cooperativa dos Produtores Rurais de Planaltina de Goiás e Região (Prorural)", "Paranoá, DF"),
    ("Cooperativa Agropecuária da Região de Brazlândia (Coopebraz)", "Brazlândia, DF"),
    ("Cooperativa Agropecuária da Região de Brazlândia (Coopebraz)", "Taguatinga, DF"),
    ("Cooperativa Agropecuária da Região de Brazlândia (Coopebraz)", "Samambaia, DF"),
    ("Cooperativa Agropecuária da Região de Brazlândia (Coopebraz)", "Recanto das Emas, DF"),
    ("Cooperativa de Agricultura Familiar Mista do Distrito Federal (Coopermista)", "Planaltina, DF"),
    ("Cooperativa dos Agricultores Familiares Ecológicos do Cerrado (Rede Terra)", "Santa Maria, DF"),
    ("Cooperativa Agrícola da Região de Planaltina (Cootagua)", "Ceilândia, DF"),
    ("Cooperativa de Serviços Ambientais, Agrícolas, Agricultura Familiar, Sociedade, Cultura e Saúde (Cooperbrasilia)", "Sobradinho, DF"),
    ("Cooperativa de Serviços Ambientais, Agrícolas, Agricultura Familiar, Sociedade, Cultura e Saúde (Cooperbrasilia)", "São Sebastião, DF"),
]

# =============================================================================
# FUNÇÃO PARA OBTENÇÃO DE COORDENADAS
# =============================================================================


def get_coordinates(address: str) -> tuple[float | None, float | None]:
    """
    Obtém as coordenadas geográficas de um endereço utilizando o serviço Nominatim.

    Parâmetros:
        address (str): Endereço para o qual se deseja obter latitude e longitude.

    Retorno:
        tuple: Latitude e longitude, ou (None, None) se falhar.
    """
    geolocator = Nominatim(user_agent="meu_app_localizacao")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        print(f"[Aviso] Endereço não encontrado: {address}")
    except GeocoderTimedOut:
        print(f"[Erro] Tempo esgotado para: {address}")
    return None, None


# =============================================================================
# PROCESSAMENTO
# =============================================================================

def main() -> None:
    """
    Realiza o processo de geocodificação de endereços e salva as coordenadas
    geográficas em um arquivo CSV.
    """
    dados = []
    for nome, endereco in enderecos:
        lat, lon = get_coordinates(endereco)
        dados.append([nome, endereco, lat, lon])
        time.sleep(1)  # Delay para respeitar os limites da API

    df = pd.DataFrame(dados, columns=["Mercado", "Endereço", "Latitude", "Longitude"])
    df.to_csv("coordenadas_associacoes_df.csv", index=False, encoding="utf-8")
    print(df)


if __name__ == "__main__":
    main()
