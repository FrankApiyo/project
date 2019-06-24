from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import DateField
from wtforms import validators
from wtforms.fields import StringField
from wtforms.fields import SelectField


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
    phone = StringField("phone", validators=[validators.regexp('[0-9]+', message="phone number not valid"),
                                             validators.DataRequired(message="phone number required"),
                                             validators.length(min=10, max=10, message="phone "
                                                                                       "number "
                                                                                       "must "
                                                                                       "contain "
                                                                                       "10 "
                                                                                       "digits "
                                                                                       "in teh"
                                                                                       "")])
    submit = SubmitField('submit')
    #accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class DriverRegistrationForm(TravelerRegistrationForm):
    # TODO find out how to get and store the signature of drivers
    pass


class ExecRegistrationForm(TravelerRegistrationForm):
    # TODO find out how to get and store the signature of execs
    #TODO update regular expression to allow spaces in position name
    position = StringField("position", validators=[validators.regexp('[a-zA-Z]+', message="first name not "
                                                                                                "valid"),
                                                         validators.DataRequired()])


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
    phone = StringField("phone", validators=[validators.regexp('[0-9]+', message="phone number not valid"),
                                       validators.DataRequired(), validators.length(min=10, max=10, message="phone "
                                                                                                            "number "
                                                                                                            "must "
                                                                                                            "contain "
                                                                                                            "10 "
                                                                                                            "digits "
                                                                                                            "in teh"
                                                                                                            "")])
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
    pass


class NewMatatuForm(FlaskForm):
    #TODO add regular expression to validate registration
    registration = StringField("registration",  validators=[validators.DataRequired()])
    seats = StringField("seats",  validators=[validators.regexp('[0-9]+', message="number of seats not valid"),
                                                           validators.DataRequired()])


class NewRoutePriceForm(FlaskForm):
    locations = []

    price = StringField("price",  validators=[validators.regexp('[0-9]+', message="price not valid"),
                                                           validators.DataRequired()])
    route_number = StringField("route_number", validators=[validators.regexp('[0-9]+', message="price not valid"),
                                                           validators.DataRequired()])

