from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,EmailField,BooleanField
from wtforms.validators import DataRequired,length,Email,EqualTo
from flask_wtf.file import FileField,FileAllowed,FileRequired

class LoginForm(FlaskForm):
    username=StringField('username',validators=[DataRequired(message='please enter username'),length(max=8)])
    email=EmailField('email',validators=[DataRequired(message='please enter a email'),Email(message='please enter a valid email')])
    confirm_password=PasswordField('confirm password',validators=[DataRequired(message='please enter a password')])
    password=PasswordField('password',validators=[DataRequired(message='please enter password'),length(min=8),EqualTo('confirm_password',message='password do not match')])
    submit=SubmitField('login')

class BreakoutForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image = FileField(validators=[FileRequired(),FileAllowed(['jpg','jpeg','png','We only allow images'])])
    # status = BooleanField('status',validators=[DataRequired()])
    submit =(SubmitField('Add Topic!'))