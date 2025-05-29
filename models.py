from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    preferencias = db.Column(db.String(255), nullable=False)
    dist_max_km = db.Column(db.Float, nullable=False)
    endereco = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)  
    data_preferencia = db.Column(db.Date, nullable=True)
    prefere_organicos = db.Column(db.Integer, nullable=False, default=0)

class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(100))
    produtor = db.Column(db.String(100))
    nota = db.Column(db.Integer)
    comentario = db.Column(db.Text)

class Produtor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    produtos = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
