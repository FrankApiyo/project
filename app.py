from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import session
from flask_sqlalchemy import SQLAlchemy
from config import DevConfig
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from forms import TravelerRegistrationForm
from forms import TravelerLoginForm
from forms import BookSeatForm
from user import User
from passwordHelper import validate_password
from passwordHelper import get_salt
from passwordHelper import get_hash


#TODO show user who's logged in on the screen

import datetime

app = Flask(__name__)
app.config.from_object(DevConfig)
app.config['DEBUG'] = True
app.secret_key = "81kAr5ENcPvBDbJVHa9pwb5WJevwRjwtODBcNWLWsN5IznEIXJXp2jzQfqwLXxnbDRYCUAzb2Z3NHz9ov1lHKzSXC4RK7cMDo"
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
login_manager = LoginManager(app)

from models import db, Ticket, Matatu, Traveler, Location, Route, Service, Driver, Exec, Log, Event


###helper functions
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


###route functions
@app.route("/")
def home():
    #TODO add landing page
    #check if someone is already logged in and as what
    return "try /login"


@app.route("/account")
@login_required
def account():
    return render_template("user_home.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    form = TravelerLoginForm(request.form)
    if request.method == "GET":
        return render_template("login.html", form=form)
    elif request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        user_password = get_user(email)[1].password
        salt = get_user(email)[1].salt
        if user_password and validate_password(password, salt, user_password):
            user = User(email)
            login_user(user)
            ##TODO depending on who logged in redirect to a different account
            return redirect(url_for('account'))
        else:
            return redirect(url_for('login'))
    else:
        #TODO add error pages
        return "error page"
@login_required
@app.route("/payment")
def payment():
    return render_template("payment.html")

@login_required
@app.route("/history")
def history():
    traveler = Traveler.query.filter_by(email=current_user.get_id()).first()
    tickets = Ticket.query.filter_by(traveler=traveler.id).all()
    #route = Route(2, "Nairobi", "Nakuru")
    #ticket  = Ticket(None, None, None, None, None, None, None, route)
    #ticket.id = 2323
    #route2 = Route(2, "Nairobi", "Gilgil")
    #ticket2 = Ticket(None, None, None, None, None, None, None, route2)
    #ticket2.id = 8978
    #tickets.append(ticket)
    #tickets.append(ticket2)
    return render_template("history.html", tickets=tickets)

@login_required
@app.route("/no_routes")
def no_routes():
    return render_template("no_routes.html")

@login_required
@app.route("/select_matatu", methods=["POST", "GET"])
def select_matatu():
    #look in db for routes that have this to and from
    #first we have to look if such locations exist from the locations table and place it in routes
    from_locations = Location.query.filter_by(name=session["departure"]).all()
    to_locations = Location.query.filter_by(name=session["destination"]).all()
    routes = []
    for from_location in from_locations:
        for to_location in to_locations:
            rs = Route.query.filter_by(from_location=from_location.id, to_location=from_location.id).all()
            for r in rs:
                routes.append(r)
    if len(routes) <= 0:
        return redirect(url_for("no_routes"))
    else:
        # TODO we now have to list all the matatus on that route
        return "i really don't know what happened"
        #show routes found and then show matatus available for that route after user selects route
    #otherwise show users that there is no

@login_required
@app.route("/book", methods=["POST", "GET"])
def book():
    form = BookSeatForm(request.form)
    if request.method == "GET":
        return render_template("book.html", form=form)
    elif request.method == "POST" and form.validate():
        destination = form.destination.data
        departure = form.departure.data
        date = form.date.data
        time = form.time.data
        datetime_object = datetime.datetime.strptime(date+" "+time, '%b %d, %Y %I:%M %p')
        #add all the date collected here to a session
        session["datetime_object"] = datetime_object
        session["destination"] = destination
        session["departure"] = departure
        #TODO redirect to select_matatu
        return redirect(url_for("select_matatu"))
    else:
        # TODO add error pages
        print("\n\n")
        print(form.errors)
        print("\n\n")
        return "error page"


@login_required
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
        middle_name = form.middle_name.data
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
        login_user(User(email))

        return redirect(url_for('account'))

    else:
        return render_template("register.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    user = get_user(user_id)
    user_password = ""
    if user:
        user_password = user[1].email
    if user_password:
        return User(user_id)