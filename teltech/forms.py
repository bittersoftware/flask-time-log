from datetime import date, datetime
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from teltech.models import User

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])  

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired()])
    
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That user name is taken, please choose a different one")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("That email name is taken, please use a different one")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired()])

    remember = BooleanField("Remember Me")

    submit = SubmitField("Login")

class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])  

    email = StringField("Email", validators=[DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That user name is taken, please choose a different one")

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError("That email name is taken, please use a different one")

class TimeExpenseForm(FlaskForm):
    project_list = ['Clould Chile - Project A', 'Clould Spain - Project B', 'PRJ-CLD-2020'] 
    
    project = SelectField('Project', choices=project_list, default=1, validators=[DataRequired()])

    start_date = DateField('Start Date', format='%d/%m/%Y', default=date.today, validators=[DataRequired()])
    
    end_date = DateField('End Date', format='%d/%m/%Y', default=date.today, validators=[DataRequired()])
    
    hours_worked = FloatField('Hours Worked (h)', validators=[DataRequired(), NumberRange(min=0)])
    
    description = TextAreaField("Description", validators=[DataRequired()], render_kw={"placeholder": "Description of the task"})

    submit = SubmitField("Save")

    def validate_start_date(self, start_date):
        if start_date.data > self.end_date.data:
            raise ValidationError("Start Date can't be greater than End Date")

class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])

    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email. You must register first")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Reset Password")