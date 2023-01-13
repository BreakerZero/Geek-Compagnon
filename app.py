# -*- coding: utf-8 -*-
import sqlalchemy_searchable
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_caching import Cache
import sqlalchemy as sa  # ORM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm, or_, and_, select, join, outerjoin, func
from sqlalchemy_searchable import make_searchable, search
from flask_wtf import FlaskForm  # CSRF protection
from flask_mailman import Mail  # API for sending emails
from flask_cors import CORS  # prevent CORS attacks
from flask_bcrypt import Bcrypt  # hash passwords
from flask_login import LoginManager  # user session management
from huey import RedisHuey, crontab  # task queue
from flask_ipban import IpBan  # IP ban
import datetime
from sqlalchemy import literal_column
from sqlalchemy.sql.operators import op
import os
import sqlalchemy.sql.functions
import recommandation
from sqlalchemy_utils.types.pg_composite import psycopg2
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from flask_assets import Bundle, Environment

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 86400,  # 24 hours cache timeout
    'SERVER_NAME': 'geek-compagnon.io:5000',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'postgresql://claire:XR9V9vAwXX@192.168.1.9:5432/gk',
}

Base = sqlalchemy.orm.declarative_base()
login_manager = LoginManager()
make_searchable(Base.metadata)  # this is needed for the search to work
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], pool_size=30, max_overflow=0)
sa.orm.configure_mappers()
ip_ban = IpBan(ban_count=30, ban_seconds=3600*24)
ip_ban.init_app(app)
ip_ban.ip_whitelist_add('127.0.0.1')
session = orm.scoped_session(orm.sessionmaker(bind=engine))
mail = Mail(app)
cors = CORS(app)
bcrypt = Bcrypt(app)
login_manager.init_app(app)
assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css")
assets.register("css", css)
css.build()

@app.errorhandler(413)
def too_large(e):
    return "Fichier trop volumineux", 413

@login_manager.user_loader
def load_user(pseudo):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Utilisateurs.query.get(str(pseudo))

class Utilisateurs(Base):
    __tablename__ = 'utilisateurs'
    pseudo = sa.Column(sa.String, primary_key=True, nullable=False)
    mail = sa.Column(sa.String, unique=True, nullable=False)
    hash_mdp = sa.Column(sa.String, nullable=False)
    url_image = sa.Column(sa.String, nullable=False, default='default-profile.jpg')
    experience = sa.Column(sa.Integer, nullable=False, default=0)
    notification = sa.Column(sa.Boolean, nullable=False, default=False)
    date_creation = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    admin = sa.Column(sa.Boolean, nullable=False, default=False)
    fondateur = sa.Column(sa.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Utilisateur('{self.pseudo}')"

class Types_Media(Base):
    __tablename__ = 'types_media'
    nom_types_media = sa.Column(sa.Integer, primary_key=True, nullable=False)

    def __repr__(self):
        return f"Types_Media('{self.nom_types_media}')"

class Notes(Base):
    __tablename__ = 'notes'
    id_notes = sa.Column(sa.Integer, primary_key=True, nullable=False)
    note_0 = sa.Column(sa.Integer, nullable=False, default=0)
    note_1 = sa.Column(sa.Integer, nullable=False, default=0)
    note_2 = sa.Column(sa.Integer, nullable=False, default=0)
    note_3 = sa.Column(sa.Integer, nullable=False, default=0)
    note_4 = sa.Column(sa.Integer, nullable=False, default=0)
    note_5 = sa.Column(sa.Integer, nullable=False, default=0)
    note_6 = sa.Column(sa.Integer, nullable=False, default=0)
    note_7 = sa.Column(sa.Integer, nullable=False, default=0)
    note_8 = sa.Column(sa.Integer, nullable=False, default=0)
    note_9 = sa.Column(sa.Integer, nullable=False, default=0)
    note_10 = sa.Column(sa.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Notes('{self.id_notes}')"

class Fiches(Base):
    __tablename__ = 'fiches'
    id_fiches = sa.Column(sa.Integer, primary_key=True, nullable=False)
    nom = sa.Column(sa.String, nullable=False)
    synopsis = sa.Column(sa.String, nullable=False)
    cmpt_note = sa.Column(sa.Integer, nullable=False, default=0)
    moy_note = sa.Column(sa.Float, nullable=False, default=0)
    cmpt_favori = sa.Column(sa.Integer, nullable=False, default=0)
    consultation = sa.Column(sa.Integer, nullable=False, default=0)
    contributeur = sa.Column(sa.String, sa.ForeignKey('utilisateurs.Pseudo'), nullable=False)
    url_image = sa.Column(sa.String, nullable=False, default='default.jpg')
    adulte = sa.Column(sa.Boolean, nullable=False, default=False)
    info = sa.Column(sa.String, nullable=False, default='')
    concepteur = sa.Column(sa.String, nullable=False, default='')

    def __repr__(self):
        return f"Fiches('{self.nom}+{self.synopsis}')"

class Succes(Base):
    __tablename__ = 'succes'
    titre = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return f"Succes('{self.Titre}')"

class Avis(Base):
    __tablename__ = 'avis'
    id_avis = sa.Column(sa.Integer, primary_key=True, nullable=False)
    trop_popularite = sa.Column(sa.Integer, nullable=False, default=0)
    neutre_popularite = sa.Column(sa.Integer, nullable=False, default=0)
    manque_popularite = sa.Column(sa.Integer, nullable=False, default=0)
    trop_cote = sa.Column(sa.Integer, nullable=False, default=0)
    neutre_cote = sa.Column(sa.Integer, nullable=False, default=0)
    manque_cote = sa.Column(sa.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Avis('{self.ID_Avis}')"

class Noms_Alternatifs(Base):
    __tablename__ = 'noms_alternatifs'
    id_noms_alternatifs = sa.Column(sa.Integer, primary_key=True, nullable=False)
    nom_alternatif = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return f"Noms_Alternatifs('{self.id_noms_alternatifs}')"

class EAN13(Base):
    __tablename__ = 'ean13'
    ean13 = sa.Column(sa.SMALLINT, primary_key=True, nullable=False)
    limite = sa.Column(sa.Boolean, nullable=False, default=False)
    collector = sa.Column(sa.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"EAN13('{self.ean13}')"

class Genres(Base):
    __tablename__ = 'genres'
    nom_genres = sa.Column(sa.String, primary_key=True, nullable=False)

    def __repr__(self):
        return f"Genres('{self.nom_genres}')"

class Etre_Associe(Base):
    __tablename__ = 'etre_associe'
    nom_genres = sa.Column(sa.String, sa.ForeignKey('genres.nom_genres'), primary_key=True, nullable=False)
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Associes('{self.nom_genres}+{self.nom_types_media}')"

class Threads(Base):
    __tablename__ = 'threads'
    id_threads = sa.Column(sa.Integer, primary_key=True, nullable=False)
    titre = sa.Column(sa.String, nullable=False)
    date_creation = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), nullable=False)

    def __repr__(self):
        return f"Threads('{self.ID_Threads}')"

class Commentaires(Base):
    __tablename__ = 'commentaires'
    id_commentaires = sa.Column(sa.Integer, primary_key=True, nullable=False)
    date_post = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    contenu = sa.Column(sa.String, nullable=False)
    spoiler = sa.Column(sa.Boolean, nullable=False, default=False)
    adulte = sa.Column(sa.Boolean, nullable=False, default=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), nullable=False)

    def __repr__(self):
        return f"Commentaires('{self.id_commentaires}')"

class Avoir(Base):
    __tablename__ = 'avoir'
    id_commentaires = sa.Column(sa.Integer, sa.ForeignKey('commentaires.id_commentaires'), primary_key=True, nullable=False)
    id_threads = sa.Column(sa.Integer, sa.ForeignKey('threads.id_threads'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Avoir('{self.id_commentaires}'+{self.id_threads}')"

class Produits_Culturels(Base):
    __tablename__ = 'produits_culturels'
    id_produits_culturels = sa.Column(sa.Integer, primary_key=True, nullable=False)
    date_sortie = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    id_notes = sa.Column(sa.Integer, sa.ForeignKey('notes.id_notes'), nullable=False)
    id_avis = sa.Column(sa.Integer, sa.ForeignKey('avis.id_avis'), nullable=False)
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)

    def __repr__(self):
        return f"Produits_Culturels('{self.ID_Produits_Culturels}')"

class Projets_Medias(Base):
    __tablename__ = 'projets_medias'
    id_projets_medias = sa.Column(sa.Integer, primary_key=True, nullable=False)
    id_notes = sa.Column(sa.Integer, sa.ForeignKey('notes.id_notes'), nullable=False)
    id_avis = sa.Column(sa.Integer, sa.ForeignKey('avis.id_avis'), nullable=False)
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)

    def __repr__(self):
        return f"Projets_Medias('{self.id_projets_medias}')"

class Projets_Transmedias(Base):
    __tablename__ = 'projets_transmedias'
    id_projets_transmedias = sa.Column(sa.Integer, primary_key=True, nullable=False)
    id_notes = sa.Column(sa.Integer, sa.ForeignKey('notes.id_notes'), nullable=False)
    id_avis = sa.Column(sa.Integer, sa.ForeignKey('avis.id_avis'), nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)
    titre = sa.Column(sa.String, sa.ForeignKey('Succes.titre'), nullable=False)

    def __repr__(self):
        return f"Projets_Medias('{self.ID_Projets_Transmedias}')"

class Etre_Compose(Base):
    __tablename__ = 'etre_compose'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    ordre = sa.Column(sa.Integer, nullable=True)

    def __repr__(self):
        return f"Etre_Composes('{self.id_produits_culturels}'+{self.id_projets_medias}')"

class Contenir(Base):
    __tablename__ = 'contenir'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedia.id_projets_transmedias'), primary_key=True, nullable=False)
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Contenir('{self.id_projets_transmedias}'+{self.id_projets_medias}')"

class Nommer_T(Base):
    __tablename__ = 'nommer_t'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedia.id_projets_transmedias'), primary_key=True, nullable=False)
    id_noms_alternatifs = sa.Column(sa.Integer, sa.ForeignKey('noms_alternatifs.id_noms_alternatifs'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Nommer_T('{self.id_projets_transmedias}'+{self.id_noms_alternatifs}')"

class Nommer_M(Base):
    __tablename__ = 'nommer_m'
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    id_noms_alternatifs = sa.Column(sa.Integer, sa.ForeignKey('noms_alternatifs.id_noms_alternatifs'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Nommer_M('{self.id_projets_medias}'+{self.id_noms_alternatifs}')"

class Nommer_C(Base):
    __tablename__ = 'nommer_c'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    id_noms_alternatifs = sa.Column(sa.Integer, sa.ForeignKey('noms_alternatifs.id_noms_alternatifs'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Nommer_C('{self.id_produits_culturels}'+{self.id_noms_alternatifs}')"

class Etre_Identifie(Base):
    __tablename__ = 'etre_identifie'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    ean13 = sa.Column(sa.Integer, sa.ForeignKey('ean13.ean13'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Identifie('{self.id_produits_culturels}'+{self.ean13}')"

class Etre_Defini(Base):
    __tablename__ = 'etre_defini'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    nom_genres = sa.Column(sa.String, sa.ForeignKey('genres.nom_genres'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Defini('{self.id_produits_culturels}'+{self.nom_genres}')"

class Etre_Commente_T(Base):
    __tablename__ = 'etre_comment_t'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedia.id_projets_transmedias'), primary_key=True, nullable=False)
    id_commentaires = sa.Column(sa.Integer, sa.ForeignKey('commentaires.id_commentaires'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Comment_T('{self.id_projets_transmedias}'+{self.id_commentaires}')"

class Etre_Commente_M(Base):
    __tablename__ = 'etre_comment_m'
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    id_commentaires = sa.Column(sa.Integer, sa.ForeignKey('commentaires.id_commentaires'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Comment_M('{self.id_projets_medias}'+{self.id_commentaires}')"

class Etre_Commente_C(Base):
    __tablename__ = 'etre_comment_c'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    id_commentaires = sa.Column(sa.Integer, sa.ForeignKey('commentaires.id_commentaires'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Comment_C('{self.id_produits_culturels}'+{self.id_commentaires}')"

class Posseder_T(Base):
    __tablename__ = 'posseder_t'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedia.id_projets_transmedias'), primary_key=True, nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    favori = sa.Column(sa.Boolean, nullable=False, default=False)
    note = sa.Column(sa.SMALLINT, nullable=True)
    avis_popularite = sa.Column(sa.String(7), nullable=True)
    avis_cote = sa.Column(sa.String(7), nullable=True)

    def __repr__(self):
        return f"Posseder_T('{self.id_projets_transmedias}'+{self.pseudo}')"

class Posseder_M(Base):
    __tablename__ = 'posseder_m'
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    favori = sa.Column(sa.Boolean, nullable=False, default=False)
    note = sa.Column(sa.SMALLINT, nullable=True)
    avis_popularite = sa.Column(sa.String(7), nullable=True)
    avis_cote = sa.Column(sa.String(7), nullable=True)

    def __repr__(self):
        return f"Posseder_M('{self.id_projets_medias}'+{self.pseudo}')"

class Posseder_C(Base):
    __tablename__ = 'posseder_c'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    favori = sa.Column(sa.Boolean, nullable=False, default=False)
    note = sa.Column(sa.SMALLINT, nullable=True)
    avis_popularite = sa.Column(sa.String(7), nullable=True)
    avis_cote = sa.Column(sa.String(7), nullable=True)

    def __repr__(self):
        return f"Posseder_C('{self.id_produits_culturels}'+{self.pseudo}')"

class Moyennes(Base):
    __tablename__ = 'moyennes'
    id_moyennes = sa.Column(sa.Integer, primary_key=True, nullable=False)
    moyenne = sa.Column(sa.Float, nullable=False)
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), nullable=False)

    def __repr__(self):
        return f"Moyennes('{self.id_moyennes}'+{self.moyenne}')"

class Donner(Base):
    __tablename__ = 'donner'
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    id_moyennes = sa.Column(sa.Integer, sa.ForeignKey('moyennes.id_moyennes'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Donner('{self.pseudo}'+{self.id_moyennes}')"

class Nombre_Possession(Base):
    __tablename__ = 'nombre_possession'
    id_nombre_possession = sa.Column(sa.Integer, primary_key=True, nullable=False)
    nombre_possession = sa.Column(sa.Integer, nullable=False)
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), nullable=False)

    def __repr__(self):
        return f"Nombre_Possession('{self.id_nombre_possession}'+{self.nombre_possession}')"

class Avoir_Nombre_Possession(Base):
    __tablename__ = 'avoir_nombre_possession'
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    id_nombre_possession = sa.Column(sa.Integer, sa.ForeignKey('nombre_possession.id_nombre_possession'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Avoir_Nombre_Possession('{self.pseudo}'+{self.id_nombre_possession}')"

class Notes_Utilisateurs(Base):
    __tablename__ = 'notes_utilisateurs'
    id_notes = sa.Column(sa.Integer, sa.ForeignKey('notes.id_notes'), primary_key=True, nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), nullable=False)

    def __repr__(self):
        return f"Notes_Utilisateurs('{self.id_notes}'+{self.pseudo}+{self.nom_types_media}')"

#create a recommandation algorithm with sklearn k nearest neighbors base on data on database and return a list of recommandation
def recommandations(id_produit: int, nb_recommandations: int):
    #create a content based recommandation algorithm
    #get produit culturel, fiche, noms alternatif, genres, type media from id_produits_culturels in database
    base = (
        session.query(
            Produits_Culturels.id_produits_culturels,
            Produits_Culturels.date_sortie,
            Fiches.nom,
            Fiches.synopsis,
            Fiches.adulte,
            Fiches.concepteur,
            func.array_agg(func.distinct(Noms_Alternatifs.nom_alternatif)),
            Types_Media.nom_types_media,
            func.array_agg(func.distinct(Genres.nom_genres)),
        )
        .select_from(Produits_Culturels)
        .join(Fiches)
        .join(Etre_Defini) #ou outerjoin ?
        .join(Types_Media)
        .join(Genres) #ou outerjoin ?
        .outerjoin(Nommer_C)
        .outerjoin(Noms_Alternatifs)
        .group_by(
            Produits_Culturels.id_produits_culturels,
            Fiches.id_fiches,
            Types_Media.nom_types_media,
        )
        .all()
    )
    #create a dataframe with pandas
    df = pd.DataFrame(base, columns=["id","date_sortie", "nom", "synopsis", "adulte", "concepteur", "noms_alternatifs", "nom_types_media", "genres"])
    # Sélectionner les colonnes qui contiennent les features à utiliser pour la recommandation
    features = ['nom', 'concepteur', 'synopsis', 'nom_types_media', 'genres', 'noms_alternatifs']
    data = df[features]

    # Remplacer les valeurs null par une chaîne vide
    data = data.fillna('')

    data['genres'] = data['genres'].apply(lambda x: ' '.join(x) if type(x) == (list or None) else x)
    data['noms_alternatifs'] = data['noms_alternatifs'].apply(lambda x: ' '.join(x) if type(x) == list and x is not None else x)
    # Concaténer toutes les features en une seule colonne pour utiliser la similarité de chaîne de caractères
    data['combined_features'] = data[features].apply(lambda x: ' '.join(x), axis=1)

    # Initialiser l'objet KNN avec la distance de similarité de chaîne de caractères
    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(data['combined_features'])

    # Trouver les k plus proches voisins de l'élément donné
    distances, indices = knn.kneighbors(data[data['nom'] == "La Mélancolie de Haruhi Suzumiya"]['combined_features'], n_neighbors=nb_recommandations + 1)
    indices = indices.flatten()
    distances = distances.flatten()

    # Retourner les k plus proches voisins sauf l'élément lui-même
    return data.iloc[indices[1:]].reset_index(drop=True)









@app.route('/')
@cache.cached(timeout=24*60*60)
def index():
    nb_user = session.query(Utilisateurs).count()
    return render_template('public/index.html', nb_user=nb_user)
@app.route('/test')
def test():
    return render_template('public/test.html')
@app.route('/livesearch', methods=['GET','POST'])
def livesearch():
    title = "Haruhi"
    #escape the user input to prevent sql injection
    #search = request.form.get('search')

    if title == '':
        return render_template('public/base.html')
    else:
        print(title)
        result = session.query(Produits_Culturels.id_produits_culturels, Fiches.nom, Fiches.synopsis, Produits_Culturels.date_sortie, Fiches.url_image, Noms_Alternatifs.nom_alternatif, Types_Media.nom_types_media, Etre_Compose.ordre, Projets_Medias.id_projets_medias, Projets_Medias.nom_types_media)\
            .select_from(Produits_Culturels)\
            .join(Types_Media)\
            .outerjoin(Nommer_C, Noms_Alternatifs, Etre_Compose, Projets_Medias)\
            .filter(or_(Fiches.nom.match(title), Noms_Alternatifs.nom_alternatif.match(title)))\
            .filter(Produits_Culturels.id_fiches == Fiches.id_fiches) \
            .distinct(Produits_Culturels.id_produits_culturels).all()
        for r in result:
            print(r)
        return "ok"
@app.route('/recommandation', methods=['GET','POST'])
def recommandation():
    rec = recommandations(2, 1)
    return jsonify(rec)