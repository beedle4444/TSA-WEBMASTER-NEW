from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, SelectMultipleField, SubmitField, PasswordField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Optional
from wtforms import ValidationError
from sqlalchemy import select

from tsa_webmaster import db
from flask_login import current_user
from tsa_webmaster.models import User

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ResourceForm(FlaskForm):
    resource_title = StringField('Title', validators=[DataRequired()])
    resource_description = TextAreaField('Description', validators=[DataRequired()])
    resource_date = DateField('Date', validators=[DataRequired()])
    resource_time = TimeField('Time', validators=[DataRequired()])
    resource_location = StringField('Location', validators=[DataRequired()])
    resource_category = SelectField('Category', choices=[('volunteering', 'Volunteering'), ('education', 'Education'), ('recreation', 'Recreation'), ('misc', 'Miscellaneous')], validators=[DataRequired()])
    resource_volunteering_tags = MultiCheckboxField('Tags for Volunteering', choices=['Tutoring', 'Cleaning', 'Animal Care', 'Event Support', 'Assistance with Tasks'], validators=[Optional()])
    resource_education_tags = MultiCheckboxField('Tags for Education', choices=['Science', 'Math', 'English', 'History', 'Art', 'Music', 'Computer Science'], validators=[Optional()])
    resource_recreation_tags = MultiCheckboxField('Tags for Recreation', choices=['Sports', 'Games', 'Outdoor Activities', 'Indoor Activities', 'Group Activities'], validators=[Optional()])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        user = db.session.execute(select(User).filter_by(email=field.data)).scalar_one_or_none()
        if user:
            raise ValidationError("This email is already registered.")

    def validate_username(self, field):
        user = db.session.execute(select(User).filter_by(username=field.data)).scalar_one_or_none()
        if user:
            raise ValidationError("This username is already taken.")
        if not field.data.isalnum():
            raise ValidationError("Username cannot contain special characters.")
        if len(field.data) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if len(field.data) > 20:
            raise ValidationError("Username must be less than 20 characters long.")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')