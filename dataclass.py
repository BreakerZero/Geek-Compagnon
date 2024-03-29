import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import relationship

Base = sa.orm.declarative_base()
import datetime
from flask_login import UserMixin
class Utilisateurs(Base, UserMixin):
    __tablename__ = 'utilisateurs'
    pseudo = sa.Column(sa.String, primary_key=True, nullable=False)
    hash_mail = sa.Column(sa.String, unique=True, nullable=False)
    hash_mdp = sa.Column(sa.String, nullable=False)
    url_image = sa.Column(sa.String, nullable=False, default='/static/images/default-profile.png')
    experience = sa.Column(sa.Integer, nullable=False, default=0)
    notification = sa.Column(sa.Boolean, nullable=False, default=False)
    date_creation = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    admin = sa.Column(sa.Boolean, nullable=False, default=False)
    fondateur = sa.Column(sa.Boolean, nullable=False, default=False)
    desactive = sa.Column(sa.Boolean, nullable=False, default=False)
    date_desactive = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    verifie = sa.Column(sa.Boolean, nullable=False, default=False)
    otp_secret = sa.Column(sa.String, nullable=True)
    profil_public = sa.Column(sa.Boolean, nullable=False, default=True)
    adulte = sa.Column(sa.Boolean, nullable=False, default=False)
    biographie = sa.Column(sa.String, nullable=True)
    posseder_t = relationship("Posseder_T", backref="utilisateur", cascade="all, delete-orphan")
    posseder_m = relationship("Posseder_M", backref="utilisateur", cascade="all, delete-orphan")
    posseder_c = relationship("Posseder_C", backref="utilisateur", cascade="all, delete-orphan")
    threads = relationship("Threads", backref="utilisateur", cascade="all, delete-orphan")
    commentaires = relationship("Commentaires", backref="utilisateur", cascade="all, delete-orphan")
    notes = relationship("Notes", backref="utilisateur", cascade="all, delete-orphan")
    avis = relationship("Avis", backref="utilisateur", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Utilisateurs('{self.pseudo}')"
    def get_id(self):
        return self.pseudo

class Types_Media(Base):
    __tablename__ = 'types_media'
    nom_types_media = sa.Column(sa.Integer, primary_key=True, nullable=False)

    def __repr__(self):
        return f"Types_Media('{self.nom_types_media}')"

class Notes(Base):
    __tablename__ = 'notes'
    id_notes = sa.Column(sa.Integer, primary_key=True, nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), nullable=False)
    note = sa.Column(sa.Integer, nullable=False, default=0)
    fiche = relationship("Fiches", back_populates="notes", lazy='joined')

    def __repr__(self):
        return f"Notes('{self.id_notes}')"

class Fiches(Base):
    __tablename__ = 'fiches'
    id_fiches = sa.Column(sa.Integer, primary_key=True, nullable=False)
    nom = sa.Column(sa.String, nullable=False)
    synopsis = sa.Column(sa.String, nullable=False, default='TBA')
    consultation = sa.Column(sa.Integer, nullable=False, default=0)
    contributeur = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), nullable=False)
    url_image = sa.Column(sa.String, nullable=False, default='static/images/fiches/default.png')
    adulte = sa.Column(sa.Boolean, nullable=False, default=False)
    info = sa.Column(sa.String, nullable=False, default='')
    concepteur = sa.Column(sa.String, nullable=False, default='')
    produits_culturels = relationship("Produits_Culturels", back_populates="fiche", lazy='joined')
    projets_medias = relationship("Projets_Medias", back_populates="fiche", lazy='joined')
    projets_transmedias = relationship("Projets_Transmedias", back_populates="fiche", lazy='joined')
    notes = relationship("Notes", back_populates="fiche", lazy='joined')
    avis = relationship("Avis", back_populates="fiche", lazy='joined')

    def __repr__(self):
        return f"Fiches('{self.nom}+{self.synopsis}')"

class Succes(Base):
    __tablename__ = 'succes'
    titre = sa.Column(sa.String, primary_key=True, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    url_image = sa.Column(sa.String, nullable=False, default='/static/images/fiches/default-success.png')

    def __repr__(self):
        return f"Succes('{self.Titre}')"

class Avis(Base):
    __tablename__ = 'avis'
    id_avis = sa.Column(sa.Integer, primary_key=True, nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), nullable=False)
    favori = sa.Column(sa.Boolean, nullable=False, default=False)
    avis_popularite = sa.Column(sa.Integer, nullable=False, default=0) # 0 = neutre, 1 = like, -1 = dislike
    avis_cote = sa.Column(sa.Integer, nullable=False, default=0) # 0 = neutre, 1 = like, -1 = dislike
    fiche = relationship("Fiches", back_populates="avis", lazy='joined')

    def __repr__(self):
        return f"Avis('{self.ID_Avis}')"

class Noms_Alternatifs(Base):
    __tablename__ = 'noms_alternatifs'
    nom_alternatif = sa.Column(sa.String, primary_key=True, nullable=False)

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
        return f"Threads('{self.id_threads}')"

class Commentaires(Base):
    __tablename__ = 'commentaires'
    id_commentaires = sa.Column(sa.Integer, primary_key=True, nullable=False)
    date_post = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    contenu = sa.Column(sa.String, nullable=False)
    spoiler = sa.Column(sa.Boolean, nullable=False, default=False)
    adulte = sa.Column(sa.Boolean, nullable=False, default=False)
    signale = sa.Column(sa.Boolean, nullable=False, default=False)
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
    date_sortie = sa.Column(sa.DateTime, nullable=True, default="01/01/1900")
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)
    verifie = sa.Column(sa.Boolean, nullable=False, default=False)
    etre_compose = relationship("Etre_Compose", back_populates="produits_culturels", lazy='joined')
    fiche = relationship("Fiches", back_populates="produits_culturels", lazy='joined')

    def __repr__(self):
        return f"Produits_Culturels('{self.id_produits_culturels}')"

class Projets_Medias(Base):
    __tablename__ = 'projets_medias'
    id_projets_medias = sa.Column(sa.Integer, primary_key=True, nullable=False)
    nom_types_media = sa.Column(sa.String, sa.ForeignKey('types_media.nom_types_media'), nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)
    titre = sa.Column(sa.String, sa.ForeignKey('succes.titre'), nullable=False)
    verifie = sa.Column(sa.Boolean, nullable=False, default=False)
    etre_compose = relationship("Etre_Compose", back_populates="projets_medias", lazy='joined')
    contenir = relationship("Contenir", back_populates="projets_medias", lazy='joined')
    fiche = relationship("Fiches", back_populates="projets_medias", lazy='joined')

    def __repr__(self):
        return f"Projets_Medias('{self.id_projets_medias}')"

class Projets_Transmedias(Base):
    __tablename__ = 'projets_transmedias'
    id_projets_transmedias = sa.Column(sa.Integer, primary_key=True, nullable=False)
    id_fiches = sa.Column(sa.Integer, sa.ForeignKey('fiches.id_fiches'), nullable=False)
    titre = sa.Column(sa.String, sa.ForeignKey('succes.titre'), nullable=False)
    verifie = sa.Column(sa.Boolean, nullable=False, default=False)
    contenir = relationship("Contenir", back_populates="projets_transmedias", lazy='joined')
    fiche = relationship("Fiches", back_populates="projets_transmedias", lazy='joined')

    def __repr__(self):
        return f"Projets_Transmedias('{self.ID_Projets_Transmedias}')"

class Etre_Compose(Base):
    __tablename__ = 'etre_compose'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    ordre = sa.Column(sa.Integer, nullable=True)
    verifie = sa.Column(sa.Boolean, nullable=False, default=False)
    produits_culturels = relationship("Produits_Culturels", back_populates="etre_compose", lazy='joined')
    projets_medias = relationship("Projets_Medias", back_populates="etre_compose", lazy='joined')


    def __repr__(self):
        return f"Etre_Composes('{self.id_produits_culturels}'+{self.id_projets_medias}')"

class Contenir(Base):
    __tablename__ = 'contenir'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedias.id_projets_transmedias'), primary_key=True, nullable=False)
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    verifie = sa.Column(sa.Boolean, nullable=False, default=False)
    projets_medias = relationship("Projets_Medias", back_populates="contenir", lazy='joined')
    projets_transmedias = relationship("Projets_Transmedias", back_populates="contenir", lazy='joined')

    def __repr__(self):
        return f"Contenir('{self.id_projets_transmedias}'+{self.id_projets_medias}')"

class Nommer_T(Base):
    __tablename__ = 'nommer_t'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedias.id_projets_transmedias'), primary_key=True, nullable=False)
    nom_alternatif = sa.Column(sa.String, sa.ForeignKey('noms_alternatifs.nom_alternatif'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Nommer_T('{self.id_projets_transmedias}'+{self.id_noms_alternatifs}')"

class Nommer_M(Base):
    __tablename__ = 'nommer_m'
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    nom_alternatif = sa.Column(sa.String, sa.ForeignKey('noms_alternatifs.nom_alternatif'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Nommer_M('{self.id_projets_medias}'+{self.id_noms_alternatifs}')"

class Nommer_C(Base):
    __tablename__ = 'nommer_c'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    nom_alternatif = sa.Column(sa.String, sa.ForeignKey('noms_alternatifs.nom_alternatif'), primary_key=True, nullable=False)

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
    __tablename__ = 'etre_commente_t'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedias.id_projets_transmedias'), primary_key=True, nullable=False)
    id_commentaires = sa.Column(sa.Integer, sa.ForeignKey('commentaires.id_commentaires'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Commente_T('{self.id_projets_transmedias}'+{self.id_commentaires}')"

class Etre_Commente_M(Base):
    __tablename__ = 'etre_commente_m'
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    id_commentaires = sa.Column(sa.Integer, sa.ForeignKey('commentaires.id_commentaires'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Commente_M('{self.id_projets_medias}'+{self.id_commentaires}')"

class Etre_Commente_C(Base):
    __tablename__ = 'etre_commente_c'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    id_commentaires = sa.Column(sa.Integer, sa.ForeignKey('commentaires.id_commentaires'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Etre_Commente_C('{self.id_produits_culturels}'+{self.id_commentaires}')"

class Posseder_T(Base):
    __tablename__ = 'posseder_t'
    id_projets_transmedias = sa.Column(sa.Integer, sa.ForeignKey('projets_transmedias.id_projets_transmedias'), primary_key=True, nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    date_ajout = sa.Column(sa.TIMESTAMP, nullable=False, default=datetime.datetime.now())

    def __repr__(self):
        return f"Posseder_T('{self.id_projets_transmedias}'+{self.pseudo}')"

class Posseder_M(Base):
    __tablename__ = 'posseder_m'
    id_projets_medias = sa.Column(sa.Integer, sa.ForeignKey('projets_medias.id_projets_medias'), primary_key=True, nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    date_ajout = sa.Column(sa.TIMESTAMP, nullable=False, default=datetime.datetime.now())

    def __repr__(self):
        return f"Posseder_M('{self.id_projets_medias}'+{self.pseudo}')"

class Posseder_C(Base):
    __tablename__ = 'posseder_c'
    id_produits_culturels = sa.Column(sa.Integer, sa.ForeignKey('produits_culturels.id_produits_culturels'), primary_key=True, nullable=False)
    pseudo = sa.Column(sa.String, sa.ForeignKey('utilisateurs.pseudo'), primary_key=True, nullable=False)
    physiquement = sa.Column(sa.Boolean, nullable=False, default=True)
    souhaite = sa.Column(sa.Boolean, nullable=False, default=False)
    date_ajout = sa.Column(sa.TIMESTAMP, nullable=False, default=datetime.datetime.now())
    limite = sa.Column(sa.Boolean, nullable=False, default=False)
    collector = sa.Column(sa.Boolean, nullable=False, default=False)
    produits_culturels = relationship("Produits_Culturels", backref="possessions", lazy='joined')

    def __repr__(self):
        return f"Posseder_C('{self.id_produits_culturels}'+{self.pseudo}')"

class Temp_Secrets(Base):
    __tablename__ = 'tempsecrets'

    token = sa.Column(sa.String, primary_key=True)
    secret = sa.Column(sa.String, nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, token, secret):
        self.token = token
        self.secret = secret