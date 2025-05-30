from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Usuario, Avaliacao
from folium.plugins import MarkerCluster
from datetime import datetime
import pandas as pd
import folium
import os
import csv

from Processamento.main import gerar_recomendacoes

print("Iniciando app Flask...")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'segredo'
db.init_app(app)

# Inicializa banco de dados
with app.app_context():
    try:
        db.create_all()
        print("Banco de dados inicializado com sucesso.")
    except Exception as e:
        print("Erro ao criar o banco de dados:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/avaliar', methods=['GET', 'POST'])
def avaliar():
    # Carrega os produtores do CSV
    df = pd.read_csv("Processamento/coordenadas_associacoes_df.csv")
    produtores = sorted((df['Mercado'].str.strip() + " - " + df['Endereço'].str.strip()).unique())

    if request.method == 'POST':
        nome = request.form['nome']
        produtor = request.form['produtor']
        nota = int(request.form['nota'])
        comentario = request.form['comentario']
        avaliacao = Avaliacao(nome_usuario=nome, produtor=produtor, nota=nota, comentario=comentario)
        db.session.add(avaliacao)
        db.session.commit()
        return redirect(url_for('avaliacoes'))
    return render_template('avaliar.html', produtores=produtores)

@app.route('/avaliacoes')
def avaliacoes():
    if request.method == 'POST':
        nome = request.form['nome']
        produtor = request.form['produtor']
        nota = int(request.form['nota'])
        comentario = request.form['comentario']
        avaliacao = Avaliacao(nome_usuario=nome, produtor=produtor, nota=nota, comentario=comentario)
        db.session.add(avaliacao)
        db.session.commit()
        return redirect('/')
    
    todas = Avaliacao.query.all()
    return render_template('avaliacoes.html', avaliacoes=todas)

@app.route('/cadastrar', methods=['GET'])
def cadastrar_user():
    return render_template('cadastro_user.html')

@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    session['nome'] = request.form['nome']
    session['dist_max_km'] = float(request.form['dist_max_km'])
    session['latitude'] = request.form['latitude']
    session['longitude'] = request.form['longitude']
    session['endereco'] = request.form['endereco']
    preferencias = request.form.getlist('preferencias')
    session['preferencias_str'] = ','.join(preferencias).lower()
    data_preferencia_str = request.form.get('data_preferencia')
    session['data_preferencia'] = datetime.strptime(data_preferencia_str, '%Y-%m-%d').date()
    organicos = request.form.get('produtos_organicos')
    session['prefere_organicos'] = 1 if organicos == 'sim' else 0

    # usuario = Usuario(
    #     nome=nome,
    #     preferencias=preferencias_str,
    #     latitude=latitude,
    #     longitude=longitude,
    #     endereco=endereco,
    #     dist_max_km=dist_max_km,
    #     data_preferencia=data_preferencia,
    #     prefere_organicos=prefere_organicos
    # )

    # db.session.add(usuario)
    # db.session.commit()

    # print("Escrevendo no CSV:", usuario.id, usuario.nome)
    # caminho_csv = os.path.join(os.path.dirname(__file__), 'users.csv')
    # salvar_usuario_csv(usuario)

    flash('Registro realizado!', 'success')
    return redirect(url_for('recomendacoes'))

@app.route('/recomendacoes')
def recomendacoes():
    nome = session.get('nome')
    dist_max_km = session.get('dist_max_km')
    preferencias_str = session.get('preferencias_str', '')
    preferencias = [p.strip().capitalize() for p in preferencias_str.split(',') if p.strip()]
    organico = session.get('prefere_organicos', 0)
    endereco = session.get('endereco')
    latitude = session.get('latitude')
    longitude = session.get('longitude')
    data_preferencia = session.get('data_preferencia')
    if data_preferencia:
        if isinstance(data_preferencia, str):
            try:
                # Tenta o formato padrão
                data_preferencia = datetime.strptime(data_preferencia, '%Y-%m-%d').date()
            except ValueError:
                try:
                    # Tenta formato RFC (Wed, 11 Nov 2026 00:00:00 GMT)
                    data_preferencia = datetime.strptime(data_preferencia, '%a, %d %b %Y %H:%M:%S %Z').date()
                except ValueError:
                    # Usa pandas para tentar converter qualquer formato
                    data_preferencia = pd.to_datetime(data_preferencia).date()
        mes_atual = data_preferencia.month
    else:
        mes_atual = pd.Timestamp.now().month

    mercados = gerar_recomendacoes(
        endereco=endereco,
        itens_preferidos=preferencias,
        organico=organico,
        mes_atual=mes_atual,
        distancia_max_km=dist_max_km,
        latitude=latitude,
        longitude=longitude
    )

    print("Mercados Recomendados: ", mercados)
    
    if not mercados:
        flash('Nenhuma das suas preferências está disponível no mês selecionado. Tente outros produtos ou outra data.', 'warning')
    
    return render_template("recomendacoes.html",
                           mercados=mercados,
                           lat=latitude, lon=longitude)

@app.route('/mapa')
def mapa():    
    mapa = folium.Map(location=[-15.8, -47.9], zoom_start=11)
    cluster = MarkerCluster().add_to(mapa)

    usuario_id = request.args.get('usuario_id')
    usuario = Usuario.query.get(usuario_id)

    with open('Processamento/coordenadas_associacoes_df.csv', newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            nome_mercado = linha['Mercado']
            endereco = linha['Endereço']
            lat = float(linha['Latitude'])
            lon = float(linha['Longitude'])

            folium.Marker(
                location=[lat, lon],
                popup=f"<strong>{nome_mercado}</strong><br>Endereço: {endereco}",
                icon=folium.Icon(color='blue')
            ).add_to(cluster)

    os.makedirs('static/mapas', exist_ok=True)
    mapa.save('static/mapas/mapa.html')

    return render_template('mapa.html')


if __name__ == '__main__':
    app.run(debug=True)

print("Finalizando app Flask...")