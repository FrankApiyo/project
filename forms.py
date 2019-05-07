from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import DateField
from wtforms import validators
from wtforms.fields import StringField
from wtforms.fields import BooleanField


class TravelerRegistrationForm(FlaskForm):
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email(message="incorrect email "
                                                                                                "format"),
                                            validators.DataRequired()])
    password = PasswordField('password', validators=[validators.DataRequired(),validators.Length(min=8,
                                                                                                message="Please "
                                                                                                        "choose a "
                                                                                                        "passwordof "
                                                                                                        "at least 8 "
                                                                                                        "characters")])
    password2 = PasswordField('password2', validators=[validators.EqualTo('password',message='Passwords must match'), validators.DataRequired()])
    username = StringField("username", validators=[validators.Length(min=4, max=25, message="username must be at "
                                                                                            "least 4 characters long "
                                                                                            "and at most 25 "
                                                                                            "characters long"),
                                                   validators.DataRequired()])
    birthday = DateField("birthday", validators=[validators.DataRequired()])
    id = StringField("id", validators=[validators.regexp('[0-9]+', message="ID not valid"),
                                       validators.DataRequired(), validators.length(min=1, max=15, message="enter a "
                                                                                                      "correct id "
                                                                                                "number")])
    first_name = StringField("first_name", validators=[validators.regexp('[a-zA-Z]+', message="first name not "
                                                                                               "valid"), validators.DataRequired()])
    last_name = StringField("last_name", validators=[validators.regexp('[a-zA-Z]+', message="first name not valid"),
                                                     validators.DataRequired()])
    middle_name = StringField("middle_name", validators=[validators.regexp('[a-zA-Z]+', message="first name not "
                                                                                                 "valid"), validators.DataRequired()])
    submit = SubmitField('submit')
    #accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class DriverRegistrationForm(TravelerRegistrationForm):
    #TODO this is the same as registration for Traveler except for the matatu service
    pass


class ServiceRegistrationFor(FlaskForm):
    #TODO fill this out
    pass


class TravelerLoginForm(FlaskForm):
    #TODO add ability to log in with other accounts and capcha
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email(message="incorrect email "
                                                                                                "format"),
                                            validators.DataRequired()])

    password = PasswordField('password2', validators=[validators.EqualTo('password',message='Passwords must match'),
                                                       validators.DataRequired()])
