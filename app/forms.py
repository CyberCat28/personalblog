from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=1000)])
    contacts = TextAreaField('Контакты', validators=[Length(min=0, max=1000)])
    portfolio = TextAreaField('Портфолио', validators=[Length(min=0, max=1000)])
    submit = SubmitField('Принять')
    
    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
            
class PostForm(FlaskForm):
    body = TextAreaField('Текст поста', validators=[DataRequired(), Length(min=1, max=10000)])
    submit = SubmitField('Опубликовать')