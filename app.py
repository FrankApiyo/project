from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask_sqlalchemy import SQLAlchemy
from config import DevConfig
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from forms import TravelerRegistrationForm
from user import User
from passwordHelper import validate_password
from passwordHelper import get_salt
from passwordHelper import get_hash

app = Flask(__name__)
app.config.from_object(DevConfig)
app.secret_key = "81kAr5ENcPvBDbJVHa9pwb5WJevwRjwtODBcNWLWsN5IznEIXJXp2jzQfqwLXxnbDRYCUAzb2Z3NHz9ov1lHKzSXC4RK7cMDo"
#TODO move this to the configuration file
app.debug = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

drivers = db.Table('service_drivers',
    db.Column('service', db.Text(), db.ForeignKey('service.name')),
    db.Column('driver', db.Text(), db.ForeignKey('driver.id'))
    )

execs = db.Table('service_exec',
    db.Column('service', db.Text(), db.ForeignKey('service.name')),
    db.Column('exec', db.Text(), db.ForeignKey('exec.id'))
    )
routes = db.Table('service_route',
    db.Column('service', db.Text(), db.ForeignKey('service.name')),
    db.Column('route', db.Integer(), db.ForeignKey('route.number'))
    )


class Location(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), db.CheckConstraint("lng >= 0 and lng <= 180"), nullable=False)
    lat = db.Column(db.Float(), db.CheckConstraint("lat >= -90 and lat <= 90"), nullable=False)
    lng = db.Column(db.Float(), nullable=False)

    def __init__(self, name, lat, lng):
        self.name = name
        self.lat = lat
        self.lng =lng

    def __repr__(self):
        return "\nLocation name: '{}'\nlat: '{}'\nlng: '{}'\n".format(self.name, self.lat, self.lng)


class Route(db.Model):
    number = db.Column(db.Integer(), primary_key=True)
    from_location = db.Column(db.Integer(), db.ForeignKey("location.id"), nullable=False)
    to_location = db.Column(db.Integer(), db.ForeignKey("location.id"), nullable=False)

    def __init__(self, number, to_location, from_location):
        self.number = number
        self.from_location = from_location
        self.to_location = to_location

    def __repr__(self):
        return "\nRoute: number'{}'\nto_location: '{}'\nfrom_location: '{}'".format(self.number, self.to_location, self.from_location)


class Service(db.Model):
    name = db.Column(db.Text(), primary_key=True)
    #logo will be added later on after database is ensured to be working

    routes = db.relationship(
        'Route',
        secondary=routes,
        backref=db.backref('services', lazy='dynamic')
        )
    drivers = db.relationship(
        'Driver',
        secondary=drivers,
        backref=db.backref('services', lazy='dynamic')
        )
    execs = db.relationship(
        'Exec',
        secondary=execs,
        backref=db.backref('services', lazy='dynamic')
        )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        #add ceo and name here
        return "\nMatatu Service: '{}'\n".format(self.name)


class Matatu(db.Model):
    registration = db.Column(db.Text(), primary_key=True)
    matatu_service = db.Column(db.Text(), db.ForeignKey('service.name'), nullable=False)

    def __init___(self, registration, matatu_service):
        self.registration = registration
        self.matatu_service = matatu_service

    def __repr__(self):
        return "\n<Matatu registration:'{}', service: '{}'>\n".format(self.registration, self.matatu_service)


class Ticket(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    traveler = db.Column(db.Text(), db.ForeignKey("traveler.id"), nullable=False)
    matatu = db.Column(db.Text(), db.ForeignKey("matatu.registration"), nullable=False)
    pick_up_lat = db.Column(db.Float(), db.CheckConstraint("pick_up_lat >= -90 and pick_up_lat <= 90"), nullable=False)
    pick_up_lng = db.Column(db.Float(), db.CheckConstraint("pick_up_lng >= 0 and pick_up_lng <= 180"), nullable=False)
    driver = db.Column(db.Text(), db.ForeignKey("driver.id"), nullable=False)
    cost = db.Column(db.Float(), nullable=False)
    pick_up_time = db.Column(db.DateTime(), nullable=False)
    route = db.Column(db.Integer(), db.ForeignKey("route.number"), nullable=False)

    def __init__(self, traveler, matatu, pick_up_lat, pick_up_lng, driver, cost, pick_up_time, route):
        self.traveler = traveler
        self.matatu = matatu
        self.pick_up_lat = pick_up_lat
        self.pick_up_lng = pick_up_lng
        self.driver = driver
        self.cost = cost
        self.pick_up_time = pick_up_time
        self.route = route

    def __repr__(self):
        return "\Ticker no: {}".format(self.id)


class Person:
    user_name = db.Column(db.Text(), nullable=False)
    id = db.Column(db.Text(), primary_key=True)
    birthday = db.Column(db.DateTime())
    password = db.Column(db.Text(), nullable=False)
    first_name = db.Column(db.Text(), nullable=False)
    middle_name = db.Column(db.Text(), nullable=True)
    last_name = db.Column(db.Text(), nullable=False)
    salt = db.Column(db.Text(), nullable=False)
    email = db.Column(db.Text(), nullable=False)


class ServiceEmployee(Person):
    #why this is nullable is beause an employee can leave a service but we still would like to retain data about them
    matatu_service = db.Column(db.Text(), nullable=True)


class Exec(ServiceEmployee, db.Model):
    position = db.Column(db.Text(), nullable=True)
    matatu_service = db.Column(db.Text(), nullable=False)

    def __init__(self, username, id, birthday, matatu_service, position, password, first_name, middle_name, last_name,
                 salt, email):
        self.email = email
        self.user_name = username
        self.password = password
        self.id = id
        self.birthday = birthday
        self.matatu_service = matatu_service
        self.position = position
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.salt = salt

    def __repr__(self):
        return "\nExec name'{}'\nposition '{}'\nid '{}'\nage '{}'\nmatatu_service: '{}'\n".format(self.username,
                                                                                                  self.position, self.id, self.age, self.matatu_service)


class Traveler(Person, db.Model):
    def __init__(self, user_name, id, birthday, password, first_name, middle_name, last_name, salt, email):
        self.password = password
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.user_name = user_name
        self.id = id
        self.birthday = birthday
        self.salt = salt
        self.email = email

    def __repr__(self):
        return "\nTraveler name'{}'\nid '{}'\nage '{}'\n".format(self.username, self.id, self.age)


class Driver(ServiceEmployee, db.Model):
    def __init__(self, user_name, id, birthday, matatu_service, password, first_name, middle_name, last_name, salt,
                 email):
        self.email = email
        self.user_name = user_name
        self.password = password
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.salt = salt
        self.id = id
        self.birthday = birthday
        self.matatu_service = matatu_service

    def __repr__(self):
        return "\nDriver name'{}'\nid '{}'\nage '{}'\nmatatu_service: '{}'\n".format(self.username, self.id, self.age,
                                                                                     self.matatu_service)


class Log(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    time = db.Column(db.DateTime(), nullable=False)
    ticket = db.Column(db.Integer(), db.ForeignKey("ticket.id"), unique=True, nullable=False)
    event = db.Column(db.Text(), nullable=False, index=True)

    def __init__(self, id):
        self.id=id

    def __repr__(self):
        return "\n{} at {}\n".format(self.event, self.time)


class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), index=True, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "\nEvent: {}\nid: {}\n".format(self.name, self.id)


##here we begin routing functions

#helper functions
def get_user(email):
    traveler = Traveler.query.filter_by(email=email).first()
    driver = Driver.query.filter_by(email=email).first()
    executive = Exec.query.filter_by(email=email).first()
    if executive:
        return "exec", executive
    elif driver:
        return "driver", driver
    elif traveler:
        return "traveler", traveler
    else:
        return None


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/account")
@login_required
def account():
    return "You are logged in"


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user_password = get_user(email)[1].password
    salt = get_user(email)[1].salt
    if user_password and validate_password(password, salt, user_password):
        user = User(email)
        login_user(user)
        return redirect(url_for('account'))
    return home()


@app.route("/register_traveler", methods=["POST", "GET"])
def register_traveler():
    form = TravelerRegistrationForm(request.form)
    if request.method == "GET":
        #print("\n\n\nplease work\n\n")
        return render_template("register.html", form=form)
    elif request.method == 'POST' and form.validate():
        #print("\n\n\nplease work\n\n")
        username = form.username.data
        id_num = form.id.data
        email = form.email.data
        pw1 = form.password.data
        pw2 = form.password2.data
        birthday = form.birthday.data
        first_name = form.first_name.data
        middle_name = form.last_name.data
        last_name = form.last_name.data

        #TODO add a way to inform user about the following failures
        #TODO add try catch block around the data request operations from the database and inform the user of failures
        if not pw1 == pw2:
            return "passwords dont match"
        else:
            salt = get_salt()
            password = get_hash(salt+pw1)

        if get_user(email):
            return "user already registered with that email"

        traveler = Traveler(username, id_num, birthday, password, first_name, middle_name, last_name, salt, email)
        db.session.add(traveler)
        db.session.commit()

        return "you are now registered"

    else:
        #print("\n\n\nplease work3333333\n"+str(form.validate())+"\n\n")
        #for a in form.errors:
        #    print(str(a)+": "+str(form.errors[a]))
        return render_template("register.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    user = get_user(user_id)
    user_password = ""
    if user:
        user_password = user[1].email
    if user_password:
        return User(user_id)