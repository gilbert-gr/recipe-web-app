from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


class Register(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Register")

class Login(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Login")