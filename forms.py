from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import DateField
from wtforms import validators
from wtforms.fields import StringField
from wtforms.fields import SelectField
from wtforms.fields import TimeField

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
    # TODO find out how to get and store the signature of drivers
    pass


class ServiceRegistrationForm(FlaskForm):
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email(message="incorrect email "
                                                                                                "format"),
                                            validators.DataRequired()])
    password = PasswordField('password', validators=[validators.DataRequired(), validators.Length(min=8,
                                                                                                  message="Please "
                                                                                                          "choose a "
                                                                                                          "passwordof "
                                                                                                          "at least 8 "
                                                                                                          "characters")])
    password2 = PasswordField('password2', validators=[validators.EqualTo('password', message='Passwords must match'),
                                                       validators.DataRequired()])
    birthday = DateField("birthday", validators=[validators.DataRequired()])
    id = StringField("id", validators=[validators.regexp('[0-9]+', message="ID not valid"),
                                       validators.DataRequired(), validators.length(min=1, max=15, message="enter a "
                                                                                                           "correct id "
                                                                                                           "number")])
    first_name = StringField("first_name", validators=[validators.regexp('[a-zA-Z]+', message="first name not "
                                                                                              "valid"),
                                                       validators.DataRequired()])
    last_name = StringField("last_name", validators=[validators.regexp('[a-zA-Z]+', message="first name not valid"),
                                                     validators.DataRequired()])
    middle_name = StringField("middle_name", validators=[validators.regexp('[a-zA-Z]+', message="first name not "
                                                                                                "valid"),
                                                         validators.DataRequired()])
    exec_position = StringField("exec_position", validators=[validators.regexp('[a-zA-Z]+', message="position title "
                                                                                                    "not valid"),
                                                         validators.DataRequired()])
    service_name = StringField("service_name", validators=[validators.regexp('[a-zA-Z]+', message="service name not "
                                                                                               "valid"),
                                                         validators.DataRequired()])
    service_location = StringField("service_location", validators=[validators.regexp('[a-zA-Z]+', message="service "
                                                                                                          "location "
                                                                                                          "name"
                                                                                                          "not valid"),
                                                         validators.DataRequired()])
    submit = SubmitField('submit')


class TravelerLoginForm(FlaskForm):
    #TODO add ability to log in with other accounts and capcha
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email(message="incorrect email "
                                                                                                "format")])

    password = PasswordField('password', validators=[validators.EqualTo('password',message='Passwords must match'),
                                                       validators.DataRequired()])


class ServiceManagerLoginForm(TravelerLoginForm):
    service_name = StringField("service_name", validators=[validators.regexp('[a-zA-Z]+', message="service name not "
                                                                                                 "valid"),
                                                                            validators.DataRequired()])



class BookSeatForm(FlaskForm):
    #get the choices data from the database
    departure = SelectField(
        'departure',
        choices=[("Nakuru", "Nakuru"), ("Nairobi", "Nairobi"),  ("Mombasa", "Mombasa"), ("Kisumu", "Kisumu")],
        validators=[validators.DataRequired()]
    )
    destination = SelectField(
        'destination',
        choices=[("Nakuru", "Nakuru"), ("Nairobi", "Nairobi"),  ("Mombasa", "Mombasa"), ("Kisumu", "Kisumu")],
        validators=[validators.DataRequired()]
    )
    date = StringField("date", validators=[validators.DataRequired()],
                     render_kw={'class': 'datepicker'})
    time = StringField("time", validators=[validators.DataRequired()],
                     render_kw={'class': 'timepicker'}
                     )


class NewMatatuForm(FlaskForm):
    #TODO add regular expression to validate registration
    registration = StringField("registration",  validators=[validators.DataRequired()])
    seats = StringField("seats",  validators=[validators.regexp('[0-9]+', message="number of seats not valid"),
                                                           validators.DataRequired()])


