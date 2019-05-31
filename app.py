from flask import Flask
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import session
from flask_login import current_user
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
from forms import ServiceManagerLoginForm
from forms import ServiceRegistrationForm
from forms import NewMatatuForm
from user import User, User_Exec
from passwordHelper import validate_password
from passwordHelper import get_salt
from passwordHelper import get_hash

#TODO in order to have an easy time goin forward, use facker to fill up the database
#TODO show user who's logged in on the screen
#TODO add error pages
#TODO add relay attack prevetion to documentation
#TODO remember to add prices for each route on the routes tab

import datetime

app = Flask(__name__)
app.config.from_object(DevConfig)
app.config['DEBUG'] = True
app.secret_key = "81kAr5ENcPvBDbJVHa9pwb5WJevwRjwtODBcNWLWsN5IznEIXJXp2jzQfqwLXxnbDRYCUAzb2Z3NHz9ov1lHKzSXC4RK7cMDo"
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
login_manager = LoginManager(app)

from models import db, Ticket, Matatu, Traveler, Location, Route, Service, Driver, Exec, Log, Event, \
    RoutePriceService, MatatuQueueInstance


###helper functions
def get_user(email):
    traveler = Traveler.query.filter_by(email=email).first()
    if traveler:
        return traveler
    executive = Exec.query.filter_by(email=email).first()
    if executive:
        return executive
    driver = Driver.query.filter_by(email=email).first()
    if driver:
        return driver

###route functions
@app.route("/")
def home():
    #TODO add landing page
    #check if someone is already logged in and as what
    return "try /login"

@app.route("/manage_drivers")
@login_required
def manage_drivers():
    pass


@app.route("/manage_matatu/<registration>")
@login_required
def manage_matatu(registration):
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    #here we will be able to do the following to matatus
    #1. add driver
    #2. add matatu to queue
    #3. manage routes
    #4. delete matatu
    matatu = Matatu.query.filter_by(registration=registration).first()
    return render_template("manage_matatu.html", registration=matatu.registration)


@app.route("/new_matatu", methods=["POST", "GET"])
@login_required
def new_matatu():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    form = NewMatatuForm(request.form)
    if request.method == "GET":
        return render_template("new_matatu.html", form=form)
    elif request.method == 'POST' and form.validate():
        #TODO add flash telling user if there is a matatu registered with that registration number
        seats = form.seats.data
        registration = form.registration.data
        matatu = Matatu(registration, seats)
        matatu.service = service
        db.session.add(matatu)
        db.session.commit()
        return redirect(url_for("manage"))
    else:
        #this means that the form did not validate
        #TODO remember to add flash messages telling user why form did not validate
        return render_template("new_matatu.html", form=form)


@app.route("/manage")
@login_required
def manage():

    #this prevents other users form loging in to the wrong parts of the app
    if(session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        render_template("/login")

    matatus = service.matatus.all()
    return render_template("manage.html", matatus =matatus)

@app.route("/add_service_location/<lat>/<lng>")
@app.route("/add_service_location", defaults={"lat": None, "lng":None})
def add_service_location(lat, lng):

    if lat and lng:
        service = Service(session["service_name"], session["service_location"], lat, lng)
        exec = Exec(session["username"], session["birthday"],session["exec_position"], session["password"],
                    session["first_name"], session["middle_name"], session["last_name"], session["salt"],
                    session["email"], session["id_num"])
        service.execs.append(exec)
        db.session.add(service)
        db.session.commit()
        user = User(session["email"])
        login_user(user)
        #print("\n\nare wer here\n\n"+url_for("matrips_manager_login"))
        return redirect(url_for("matrips_manager_login"))
    else:
        return render_template("add_service_location.html")

@app.route("/register_manager_and_service", methods=["POST", "GET"])
def register_manager_and_service():
    form = ServiceRegistrationForm(request.form)
    if request.method == "GET":
        # print("\n\n\nplease work\n\n")
        return render_template("register_service.html", form=form)
    elif request.method == 'POST' and form.validate():
        # print("\n\n\nplease work\n\n")
        username = form.username.data
        id_num = form.id.data
        email = form.email.data
        pw1 = form.password.data
        pw2 = form.password2.data
        birthday = form.birthday.data
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        exec_position = form.exec_position.data
        service_name = form.service_name.data
        service_location = form.service_location.data
        # TODO add a way to inform user about the following failures
        # TODO add try catch block around the data request operations from the database and inform the user of failures
        if not pw1 == pw2:
            return "passwords dont match"
        else:
            salt = get_salt()
            password = get_hash(salt + pw1)

        exec = Exec.query.filter_by(email=email).first()
        if exec:
            # TODO add flash telling the user that someone is allready registered with that piece of info/credential
            return render_template("register_service.html", form=form)

        service = Service.query.filter_by(name="service_name").first()
        if service:
            #TODO add flash telling the user that someone is allready registered with that piece of info/credential
            return render_template("register_service.html", form=form)

        session["service_name"] = service_name
        print(service_name)
        session["username"] = username
        session["birthday"] = birthday
        session["exec_position"] = exec_position
        session["password"] = password
        session["first_name"] = first_name
        session["middle_name"] = middle_name
        session["last_name"] = last_name
        session["salt"] = salt
        session["email"] = email
        session["id_num"] = id_num
        session["service_location"] = service_location

        return redirect(url_for('add_service_location'))

    else:
        return render_template("register.html", form=form)


@app.route("/manager_logout")
@login_required
def manager_logout():
    logout_user()
    return redirect(url_for("matrips_manager_login"))


@app.route("/matrips_manager", methods=["POST", "GET"])
def matrips_manager_login():
    if current_user.is_authenticated:
        return redirect(url_for("manage"))
    else:
        form = ServiceManagerLoginForm(request.form)
        if request.method == "GET":
            return render_template("manager_login.html", form=form)
        elif request.method == 'POST' and form.validate():
            service_name = form.service_name.data
            email = form.email.data
            password = form.password.data
            exec = Exec.query.filter_by(email=email).first()
            if(exec):
                user_password = exec.password
            else:
                return redirect(url_for('matrips_manager_login'))

            salt = exec.salt
            if user_password and validate_password(password, salt, user_password):
                session["service_name"] = service_name
                service = Service.query.filter_by(name=service_name).first()
                if(service):
                    exec = Exec.query.filter_by(email=email).first()
                else:
                    #TODO remember to add flash messages that tell the users what went down here
                    return redirect(url_for('matrips_manager_login'))
                if exec in service.execs:
                    user = User(email)
                    print(user)
                    login_user(user)
                    return redirect(url_for('manage'))
                else:
                    return redirect(url_for('matrips_manager_login'))
            else:
                return redirect(url_for('matrips_manager_login'))
        else:
            # TODO add error pages
            return "error page"


@app.route("/account")
@login_required
def account():
    return render_template("user_home.html")


@app.route("/ticket/<seat_number>")
@login_required
def ticket(seat_number):
    route_price_service = RoutePriceService.query.filter_by(id=session["route_price_service"]).first()
    route_price_service.matatu_queue_entry.no_of_vacant_seats -=1
    db.session.commit()
    traveler = Traveler.query.filter_by(email=current_user.get_id()).first()
    service = Service.query.filter_by(name=session["service"]).first()
    print(service)
    service_location = None
    for location in service.locations:
        if location.town == session["departure"]:
            service_location = location

    ticket = Ticket(traveler.id, route_price_service.matatu_queue_entry.matatu.registration, service_location.lat,
                    service_location.lng,
                    None, route_price_service.price,
                    route_price_service.route.number)
    db.session.add(ticket)
    db.session.commit()

    return "some other thing"


@app.route("/pick_a_seat/<id>")
@login_required
def pick_a_seat(id):
    #remember that id is the route_price_service.id that we are about to purchase
    #TODO we need to pick a seat and update the tacken seats table and matatuQueue instance table
    route_price_service = RoutePriceService.query.filter_by(id=id).first()
    no = route_price_service.matatu_queue_entry.no_of_vacant_seats
    session["route_price_service"] = route_price_service.id
    return render_template("pick_a_seat.html", no=no, range=range)


@app.route("/service/<service_name>/<destination>")
@login_required
def service(service_name, destination):
    service_name = service_name.replace("_", " ")
    session["service"] = service_name
    service = Service.query.filter_by(name=service_name).first()
    route_price_services = service.route_prices.all()
    route_price_services_to_destination = []
    #prepare a link for each list item in above list
    base_link = "/pick_a_seat/"
    link_list = []
    matatu_available_list = []
    for route_price_service in route_price_services:
        if route_price_service.route.to_town == "Nairobi":
            route_price_services_to_destination.append(route_price_service)
            link_list.append(base_link+str(route_price_service.id))
            if route_price_service.matatu_queue_entry:
                matatu_available_list.append(True)
            else:
                matatu_available_list.append(False)
    return render_template("list_routes.html", route_price_services=route_price_services_to_destination,
                           link_list=link_list, zip=zip, matatu_available_list=matatu_available_list)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("account"))
    else:
        form = TravelerLoginForm(request.form)
        if request.method == "GET":
            return render_template("login.html", form=form)
        elif request.method == 'POST' and form.validate():
            email = form.email.data
            password = form.password.data
            user_password = Traveler.query.filter_by(email=email).first().password
            salt = Traveler.query.filter_by(email=email).first().salt
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
    # route = Route(2, "Nairobi", "Nakuru")
    #ticket  = Ticket(None, None, None, None, None, None, None, route)
    #ticket.id = 2323
    #route2 = Route(2, "Nairobi", "Gilgil")
    #ticket2 = Ticket(None, None, None, None, None, None, None, route2)
    #ticket2.id = 8978
    #tickets.append(ticket)
    #tickets.append(ticket2)
    return render_template("history.html", tickets=tickets)

@login_required
@app.route("/dissapointment/<message>")
def dissapointment(message):
    return render_template("dissapointment.html", message=message)

@login_required
@app.route("/select_matatu", methods=["POST", "GET"])
def select_matatu():
    #look in db for routes that have this to and from
    routes = Route.query.filter_by(from_town=session["departure"]).filter_by(to_town=session["destination"]).all()
    route_price_services = []
    for route in routes:
        route_price_services.extend(routes[0].route_prices.all())

    services = []
    for route_price_service in route_price_services:
        #find services
        services.append(route_price_service.service)

    if len(routes) <= 0:
        return redirect(url_for("dissapointment", message="we did not find routes for that pair or departure and "
                                                          "destination"))
    elif len(services) <= 0:
        return redirect(url_for("dissapointment", message="we did not find any services for any route of that pair or "
                                                          "departure and "
                                                          "destination"))
    #TODO how can we ensure that we aren't hoping a location does not have more that one service
    #TODO change that dropdown on book page to a textfield
    urls = [];
    locations = []
    services_here = []
    for service in services:
        for location in service.locations:
            print(location)
            print(location.town)
            print(session["departure"])
            print(location.town.lower() == session["departure"].lower())
            if location.town.lower() == session["departure"].lower():
                urls.append("service/" + service.name.replace(" ", "_") + "/" + session['destination'])
                services_here.append(service.name)
                locations.append(location)
                print(location)
    else:
        # TODO we now have to list all the matatus on that route
        return render_template("services.html", locations=locations, services_here=services_here, zip=zip,
                               where_to=session['destination'], urls=urls)
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
        datetime_object = datetime.datetime.strptime(date+" "+time, '%b %d, %Y %H:%M')
        print(datetime_object)
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

        user = Traveler.query.filter_by(email=email).first()
        if user:
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
        user_password = user.email
    if user_password:
        return User(user_id)

