from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    """Formulaire d'inscription pour créer un nouveau compte utilisateur"""
    username = StringField('Nom d\'utilisateur', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', 
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirmer mot de passe', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('S\'inscrire')
    
    def validate_username(self, username):
        """Vérifie que le nom d'utilisateur n'est pas déjà utilisé"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.')
    
    def validate_email(self, email):
        """Vérifie que l'email n'est pas déjà utilisé"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà associé à un compte. Veuillez en utiliser un autre.')

class LoginForm(FlaskForm):
    """Formulaire de connexion pour les utilisateurs existants"""
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', 
                             validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class SaveTopologyForm(FlaskForm):
    """Formulaire pour sauvegarder une disposition de topologie réseau"""
    name = StringField('Nom de la disposition', 
                       validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Sauvegarder')