from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Usuario, Avaliacao
from folium.plugins import MarkerCluster
from datetime import datetime
from pandas import pd
import folium
import os
import csv

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

@app.route('/avaliar')
def avaliar():
    return render_template('avaliar.html')

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
    organicos = request.form.get('organicos')
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
    return redirect(url_for('mapa'))

@app.route('/recomendacoes')
def recomendacoes():
    # Dados do usuário
    nome = session.get('nome')
    dist_max_km = session.get('dist_max_km')
    preferencias = session.get('preferencias')
    organico = session.get('organico')
    endereco = session.get('endereco')
    latitude = session.get('latitude')
    longitude = session.get('longitude')
    mes_atual = pd.Timestamp.now().month

    return render_template("recomendacoes.html",
                           mercados=df_recomendados.to_dict(orient="records"),
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