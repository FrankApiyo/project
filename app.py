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
from user import User
from passwordHelper import validate_password
from passwordHelper import get_salt
from passwordHelper import get_hash

from lipanampesa import lipa_na_mpesa
import json


from wtforms import validators
from wtforms.fields import SelectField

#TODO in order to have an easy time goin forward, use facker to fill up the database
#TODO show user who's logged in on the screen
#TODO add error pages
#TODO add relay attack prevetion to documentation
#TODO remember to add prices for each route on the routes tab
#TODO register everyone as a traveler

import datetime
app = Flask(__name__)
app.config.from_object(DevConfig)
app.config['DEBUG'] = True
app.secret_key = "81kAr5ENcPvBDbJVHa9pwb5WJevwRjwtODBcNWLWsN5IznEIXJXp2jzQfqwLXxnbDRYCUAzb2Z3NHz9ov1lHKzSXC4RK7cMDo"
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
login_manager = LoginManager(app)

from models import db, Ticket, Matatu, Traveler, Location, Route, Service, Driver, Exec, Log, Event, \
    RoutePriceService, MatatuQueueInstance, TakenSeatInstance

from forms import TravelerRegistrationForm
from forms import TravelerLoginForm
from forms import BookSeatForm
from forms import ServiceManagerLoginForm
from forms import ServiceRegistrationForm
from forms import NewMatatuForm
from forms import DriverRegistrationForm
from forms import ExecRegistrationForm
from forms import NewRoutePriceForm
from forms import DriverLoginForm


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


@app.route("/reports")
def reports():
    return "reports"

@app.route("/driver_logout")
@login_required
def driver_logout():
    logout_user()
    return redirect(url_for("driver_login"))


@app.route("/driver_login", methods=["POST", "GET"])
def driver_login():
    if current_user.is_authenticated and session["driver_id"]:
        return redirect(url_for("/driver_dashboard"))
    else:
        form = DriverLoginForm(request.form)
        if request.method == "GET":
            return render_template("driver_login.html", form=form)
        elif request.method == 'POST' and form.validate():
            email = form.email.data
            password = form.password.data
            user_password = Driver.query.filter_by(email=email).first().password
            salt = Driver.query.filter_by(email=email).first().salt
            if user_password and validate_password(password, salt, user_password):
                user = User(email)
                login_user(user)
                ##TODO depending on who logged in redirect to a different account
                return redirect(url_for('driver_dash'))
            else:
                return redirect(url_for('driver_login'))
        else:
            #TODO add error pages
            return "error page"


@app.route("/driver_dashboard")
@login_required
def driver_dash():
    if not session["driver_id"]:
        redirect(url_for("driver_login"))
    driver = Driver.query.first();
    session["driver_id"] = driver.id
    matatu = Matatu.query.filter_by(driver_id=driver.id).first()
    if matatu:
        return redirect("/manage_matatu_queue/"+matatu.registration)
    else:
        return render_template("driver_dash.html", no_matatu=True, driver=driver)


@app.route("/add_routes", methods=["POST", "GET"])
@login_required
def add_routes():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    locations = service.locations
    NewRoutePriceForm.to_location = SelectField("to location",
                                                choices=[(str(location.id), str(location.town) + ", " + str(location.specific_location))for location in locations],
                                                validators=[validators.DataRequired()]
                                                )
    NewRoutePriceForm.from_location = SelectField("from location",
                                                  choices=[(str(location.id), str(location.town) + ", " + str(location.specific_location))for location in locations],
                                                  validators=[validators.DataRequired()]
                                                  )
    form = NewRoutePriceForm(request.form)

    if request.method == "GET":
        return render_template("new_route.html", form=form)
    elif request.method == 'POST' and form.validate():
        price = form.price.data
        route_number = form.route_number.data
        from_location = form.from_location.data
        print(from_location)
        to_location = form.to_location.data
        print(to_location)
        route_price_service = RoutePriceService(price)
        route_in_table = Route.query.filter_by(to_town_id=to_location).filter_by(
            from_town_id=from_location).filter_by(
            number=route_number).first()

        route_number_in_table = False
        for route_price in service.route_prices:
            if route_price.route.number == route_number:
                route_number_in_table = True

        if route_in_table or route_number_in_table:
            #TODO find a way to tell the user that the route number is already in the service routes
            return redirect(url_for("routes"))
        route = Route(route_number, to_location, from_location)
        route_price_service.route = route
        service.route_prices.append(route_price_service)
        db.session.add(route)
        db.session.add(route_price_service)
        print(route)
        db.session.commit()

        return redirect(url_for("routes"))
    else:
        # this means that the form did not validate
        # TODO remember to add flash messages telling user why form did not validate
        return render_template("new_route.html", form=form)


@app.route("/routes")
@login_required
def routes():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if session["service_name"]:
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    route_prices = service.route_prices.all()
    from_locations = []
    to_locations = []
    for route_price in route_prices:
        from_location = Location.query.filter_by(id=route_price.route.from_town_id).first()
        from_locations.append(from_location)
        to_location = Location.query.filter_by(id=route_price.route.to_town_id).first()
        to_locations.append(to_location)

    print(route_prices)
    return render_template("routes.html", route_price_services=route_prices, from_locations=from_locations,
                           to_locations=to_locations, zip=zip)


@app.route("/add_location/<lat>/<lng>/<specific_location>/<town>")
@app.route("/add_location", defaults={"lat": None, "lng": None, "specific_location": None, "town":None})
@login_required
def add_location(lat, lng, specific_location, town):
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if session["service_name"]:
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    if lat and lng and specific_location and town:
        town = town.strip().replace("_", " ")
        specific_location = specific_location.strip().replace("_", " ")
        location = Location(town, specific_location, lat, lng)
        service.locations.append(location)
        db.session.add(service)
        db.session.commit()
        return redirect(url_for("manage_locations"))

    return render_template("add_location.html")


@app.route("/manage_locations")
@login_required
def manage_locations():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    locations = service.locations
    return render_template("locations.html", locations=locations)

@app.route("/new_exec", methods=["POST", "GET"])
@login_required
def new_exec():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    form = ExecRegistrationForm(request.form)
    if request.method == "GET":
        return render_template("new_exec.html", form=form)
    elif request.method == 'POST' and form.validate():
        # TODO add flash telling user if there is a driver registered with that id number
        id_num = form.id.data
        email = form.email.data
        pw1 = form.password.data
        pw2 = form.password2.data
        birthday = form.birthday.data
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        position = form.position.data
        phone = form.phone.data


        # TODO add a way to inform user about the following failures
        # TODO add try catch block around the data request operations from the database and inform the user of failures
        if not pw1 == pw2:
            return render_template("new_exec.html", form=form)
        else:
            salt = get_salt()
            password = get_hash(salt + pw1)

        exec = Exec.query.filter_by(email=email).first()
        if exec:
            #TODO ADD FLASH TELLING THE USER THAT A DRIVER is already registered with that email
            return render_template("new_exec.html", form=form)
        exec = Exec(birthday, position, password, first_name, middle_name, last_name, salt, email, id_num, phone)
        db.session.add(exec)
        exec.services.append(service)
        db.session.commit()

        return redirect(url_for("manage_execs"))
    else:
        # this means that the form did not validate
        # TODO remember to add flash messages telling user why form did not validate
        return render_template("new_driver.html", form=form)

@app.route("/manage_execs")
@login_required
def manage_execs():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    execs = service.execs
    #print(drivers[0].services.all())
    return render_template("manage_execs.html", execs=execs)


@app.route("/new_driver", methods=["POST", "GET"])
@login_required
def new_driver():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    form = DriverRegistrationForm(request.form)
    if request.method == "GET":
        return render_template("new_driver.html", form=form)
    elif request.method == 'POST' and form.validate():
        # TODO add flash telling user if there is a driver registered with that id number
        id_num = form.id.data
        email = form.email.data
        pw1 = form.password.data
        pw2 = form.password2.data
        birthday = form.birthday.data
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        phone = form.phone.data

        # TODO add a way to inform user about the following failures
        # TODO add try catch block around the data request operations from the database and inform the user of failures
        if pw1 != pw2:
            return render_template("new_driver.html", form=form)
        else:
            salt = get_salt()
            password = get_hash(salt + pw1)

        driver = Driver.query.filter_by(email=email).first()
        if driver:
            #TODO ADD FLASH TELLING THE USER THAT A DRIVER is already registered with that email
            return render_template("new_driver.html", form=form)
        driver = Driver(id_num, birthday, password, first_name, middle_name, last_name, salt, email, phone)
        db.session.add(driver)
        driver.services.append(service)
        db.session.commit()

        return redirect(url_for("manage_drivers"))
    else:
        # this means that the form did not validate
        # TODO remember to add flash messages telling user why form did not validate
        return render_template("new_driver.html", form=form)


@app.route("/manage_drivers")
@login_required
def manage_drivers():
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    drivers = service.drivers
    #print(drivers[0].services.all())
    return render_template("manage_drivers.html", drivers=drivers)


@app.route("/manage_matatu_queue/<registration>/<location_id>/<route_number>/<remove>")
@app.route("/manage_matatu_queue/<registration>/<location_id>/<route_number>", defaults={"remove": None})
@app.route("/manage_matatu_queue/<registration>/<location_id>", defaults={"route_number": None, "remove": None})
@app.route("/manage_matatu_queue/<registration>", defaults={"route_number": None, "location_id": None, "remove": None})
@login_required
def manage_matatu_queue(registration, route_number, location_id, remove):
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    driver = None
    if session["service_name"]:
        service = Service.query.filter_by(name=session["service_name"]).first()
    if session["driver_id"]:
        driver = Driver.query.filter_by(id=session["driver_id"]).first()
        matatu = Matatu.query.filter_by(driver_id=driver.id).first()
        service = Service.query.filter_by(name=matatu.matatu_service).first()
        session["service_name"] = None
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    matatu = Matatu.query.filter_by(registration=registration).first()

    if remove == "-":
        #check if there are other tables that use this matatu queue entry
        print("\n\n"+str(matatu.matatu_queue_entry)+"\n\n")
        tacken_seats = TakenSeatInstance.query.filter_by(matatu_queue_instance_id=matatu.matatu_queue_entry.id).all()
        for tacken_seat in tacken_seats:
            db.session.delete(tacken_seat)

        db.session.delete(matatu.matatu_queue_entry)

        db.session.commit()
        locations = service.locations
        #print("\n\n"+str(driver)+"\n\n")
        if driver:
            return render_template("driver_dash.html", registration=matatu.registration, locations=locations,
                                driver=driver)
        return render_template("manage_matatu_queue.html", registration=matatu.registration, locations=locations)

    if location_id and not route_number:
        #ensure service has such a location
        location = Location.query.filter_by(id=location_id).first()
        if location in service.locations:
            #now show all routes from this location
            routes_from_location = []
            to_towns = []
            for route_price in service.route_prices:
                route = route_price.route
                if route.from_town_id == location.id:
                    routes_from_location.append(route)
                    to_towns.append(Location.query.filter_by(id=route.to_town_id).first())
            if driver:
                return render_template("driver_dash.html", registration=matatu.registration,
                                       routes_from_location=routes_from_location, to_towns=to_towns, zip=zip,
                                       location_id=location_id, driver=driver)
            return render_template("manage_matatu_queue.html", registration=matatu.registration,
                                   routes_from_location=routes_from_location, to_towns=to_towns, zip=zip,
                                   location_id=location_id)
    elif location_id and route_number:
        #add matatu to queue at location and at route
        matatu_queue_entry = MatatuQueueInstance.query.filter_by(matatu_registration=registration).first()
        if(matatu_queue_entry):
            if(driver):
                return render_template("driver_dash.html", registration=matatu.registration,
                                       entry=matatu.matatu_queue_entry, location_id=location_id,
                                       route_number=route_number, driver=driver)
            return render_template("manage_matatu_queue.html", registration=matatu.registration,
                                   entry=matatu.matatu_queue_entry, location_id=location_id, route_number=route_number)
        matatu_queue_entry = MatatuQueueInstance(matatu.seats)
        route_price_service = None
        route_prices = service.route_prices
        for route_price in route_prices:
            if str(route_price.route.number) == route_number and location_id == str(route_price.route.from_town_id):
                route_price_service = route_price
        matatu_queue_entry.route_price_service_id = route_price_service.id
        matatu_queue_entry.matatu_registration = matatu.registration
        db.session.add(matatu_queue_entry)
        db.session.commit()
        if(driver):
            return render_template("driver_dash.html", registration=matatu.registration,
                                   entry=matatu.matatu_queue_entry, location_id=location_id,
                                   route_number=route_number, driver=driver)
        return render_template("manage_matatu_queue.html", registration=matatu.registration,
                               entry=matatu.matatu_queue_entry, location_id=location_id, route_number=route_number)

    #a matatu can only be in one queue instance at a time
    #if matatu already on queue then just show that queue
    if matatu.matatu_queue_entry:
        #show queue
        print("adfadsf\n\n\n\n" + str(matatu.matatu_queue_entry.route_price_service_id) + "\n\n\n")
        route_price_service = RoutePriceService.query.filter_by(
            id=matatu.matatu_queue_entry.route_price_service_id).first()
        route = route_price_service.route
        if(driver):
            return render_template("driver_dash.html", registration=matatu.registration,
                                   entry=matatu.matatu_queue_entry, route_number=route.number,
                                   location_id=route.from_town_id, driver=driver)
        return render_template("manage_matatu_queue.html", registration=matatu.registration,
                               entry=matatu.matatu_queue_entry, route_number=route.number,
                               location_id=route.from_town_id)
    #else provide routes to add queue on
    else:
        #show list of locations to add matatu queue instance
        locations = service.locations
        if(driver):
            return render_template("driver_dash.html", registration=matatu.registration, locations=locations,
                                   driver=driver)
        return render_template("manage_matatu_queue.html", registration=matatu.registration, locations=locations)


@app.route("/manage_matatu_routes/<registration>/<add_or_remove>/<route_number>")
@app.route("/manage_matatu_routes/<registration>", defaults={"add_or_remove": None, "route_number": None})
@login_required
def manage_matatu_routes(registration, add_or_remove, route_number):
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if session["service_name"]:
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    matatu = Matatu.query.filter_by(registration=registration).first()

    if str(add_or_remove) == "-":
        for route in matatu.routes:
            if str(route.number) == str(route_number):
                matatu.routes.remove(route)
                db.session.commit()
                return redirect("/manage_matatu_routes/"+registration)


    elif add_or_remove == "+":
        for route_price_service in service.route_prices:
            route = route_price_service.route
            if str(route.number) == route_number and route not in matatu.routes:
                matatu.routes.append(route)
                db.session.commit()

    potential_routes = []
    for route_price_service in service.route_prices:
        route = route_price_service.route
        if not route in matatu.routes:
            potential_routes.append(route)

    return render_template("manage_matatu_routes.html", registration=matatu.registration, routes=matatu.routes,
                           potential_routes=potential_routes)



@app.route("/manage_matatu/<registration>/<add_or_remove>/<driver_id>")
@app.route("/manage_matatu/<registration>/", defaults={"driver_id": None, "add_or_remove": None})
@login_required
def manage_matatu(registration, add_or_remove, driver_id):
    # this prevents other users form loging in to the wrong parts of the app
    service = None
    if (session["service_name"]):
        service = Service.query.filter_by(name=session["service_name"]).first()
    else:
        redirect(url_for("login"))
    if not service:
        redirect(url_for("login"))

    matatu = Matatu.query.filter_by(registration=registration).first()

    if add_or_remove == "-":
        driver = Driver.query.filter_by(id=driver_id).first()
        if driver.id == matatu.driver.id:
            matatu.driver = None
            db.session.commit()

    elif add_or_remove == "+":
        driver = Driver.query.filter_by(id=driver_id).first()
        if matatu.driver is None:
            matatu.driver = driver
            db.session.commit()

    if matatu.driver:
        matatu_drivers = [matatu.driver]
        #print("matatu drivers" + str(matatu_drivers))
    potential_drivers = []
    #print("potential drivers"+str(potential_drivers))
    for driver in service.drivers:
        if not driver.matatu:
            potential_drivers.append(driver)

    #TODO find a way to tell user when we dont have a driver for the matatu
    if not matatu.driver:
        return render_template("manage_matatu.html", registration=matatu.registration,
                               potential_drivers=potential_drivers)
    else:
        return render_template("manage_matatu.html", registration=matatu.registration,
                               potential_drivers=potential_drivers, matatu_drivers=matatu_drivers)


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


@app.route("/register_manager_and_service", methods=["POST", "GET"])
def register_manager_and_service():
    form = ServiceRegistrationForm(request.form)
    if request.method == "GET":
        # print("\n\n\nplease work\n\n")
        return render_template("register_service.html", form=form)
    elif request.method == 'POST' and form.validate():
        # print("\n\n\nplease work\n\n")
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
        phone = form.phone.data
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
        service = Service(service_name)
        exec = Exec(birthday, exec_position, password, first_name, middle_name, last_name, salt, email, id_num, phone)
        service.execs.append(exec)
        db.session.add(service)
        db.session.commit()
        user = User(email)
        login_user(user)

        return redirect(url_for("matrips_manager_login"))

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
    return redirect(url_for("history"))


@app.route("/mpesa_hook", methods=["POST", "GET"])
def mpesa_hook():
    #print(str(request.data))
    data = json.loads(request.data.decode('utf-8'))
    print(data)

    if "Body" in data:
        if "stkCallback" in data["Body"]:
            if "ResultCode" in data["Body"]["stkCallback"]:
                code = data["Body"]["stkCallback"]["ResultCode"]
                print("\n\nThe code is "+str(code)+"\n\n")
                if code == 0:
                    phone = str(data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"])
                    print(phone)
                    traveler = Traveler.query.filter_by(phone=="0"+phone[3:]).first()
                    if traveler:
                        ticket = Ticket.query.filter_by(traveler=traveler.id).first()
                        if ticket:
                            payed = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
                            if ticket.balance > payed:
                                ticket.balance -= payed
                            elif ticket.balance == payed:
                                ticket.balance = 0
                                ticket.payed = True
                            else:
                                traveler.outstanding = payed - ticket.balance
                                ticket.balance = 0
                            db.session.commit()
                    #compare number and the ticket number and then set found ticket to payed if the ammount is
                    # correct, else reduce ammount and wait for balance
                    #set ticket to payed here

    message = {
        "ResponseCode": "00000000",
        "ResponseDesc": "success"
    }
    return json.dumps(message)


@app.route("/ticket/<seat_number>")
@login_required
def ticket(seat_number):
    #TODO if seat is not payed for in 1 minute, its taken away
    traveler = Traveler.query.filter_by(email=current_user.get_id()).first()
    ticket = Ticket.query.filter_by(traveler=traveler.id).first()
    if ticket:
        return redirect("/dissapointment/you haven't made your payment yet worth: "+str(ticket.cost))

    route_price_service = RoutePriceService.query.filter_by(id=session["route_price_service"]).first()
    paid = False
    balance = route_price_service.price
    if traveler.outstanding is None:
        traveler.outstanding = 0
    if int(traveler.outstanding) > 0:
        if traveler.outstanding >= route_price_service.price:
            traveler.outstanding -= route_price_service.price
            paid = True
            balance = 0;
    else:
        cost = route_price_service.price - traveler.outstanding
        balance = cost
        result = lipa_na_mpesa("254" + traveler.phone[1:], cost)
        if "ResponseCode" not in result:
            return redirect("/dissapointment/problem making payment")
        elif int(result["ResponseCode"]) != 0:
            print(result["ResponseCode"])
            return redirect("/dissapointment/problem making payment")

        route_price_service.matatu_queue_entry.no_of_vacant_seats -= 1
        db.session.commit()
        service = Service.query.filter_by(name=session["service"]).first()
        # print(service)
        service_location = None
        for location in service.locations:
            if location.town == session["departure"]:
                service_location = location

        ticket = Ticket(traveler.id, route_price_service.matatu_queue_entry.matatu.registration, service_location.lat,
                        service_location.lng,
                        None, route_price_service.price,
                        route_price_service.route.number)
        ticket.payed = paid
        ticket.balance = balance
        # mark seat at taken
        taken_seat = TakenSeatInstance(seat_number)
        taken_seat.matatu_queue_instance_id = session["matatu_queue_entry_id"]
        print(session["matatu_queue_entry_id"])
        db.session.add(taken_seat)
        # if its the last ticket available then take the matatu off the queue at location
        taken_seats = TakenSeatInstance.query.filter_by(matatu_queue_instance_id=session["matatu_queue_entry_id"]).all()
        db.session.add(ticket)
        if len(taken_seats) == session["no"]:
            db.session.delete(MatatuQueueInstance.query.filter_by(id=taken_seat.matatu_queue_instance_id))
            for seat in taken_seats:
                db.session.delete(seat)
        db.session.commit()

        return redirect(url_for("history"))






@app.route("/pick_a_seat/<id>")
@login_required
def pick_a_seat(id):
    #remember that id is the route_price_service.id that we are about to purchase
    #TODO we need to pick a seat and update the tacken seats table and matatuQueue instance table
    route_price_service = RoutePriceService.query.filter_by(id=id).first()
    no = route_price_service.matatu_queue_entry.matatu.seats
    session["no"]  = no
    session["route_price_service"] = route_price_service.id
    seat_numbers = []
    for i in range(no):
        seat_numbers.append(i)
    #default to true for all seats
    available_seats = [True for i in seat_numbers]
    #if seat is tacken then set available seat to false
    matatu_queue_entry_id = route_price_service.matatu_queue_entry.id
    taken_seats = TakenSeatInstance.query.filter_by(matatu_queue_instance_id=matatu_queue_entry_id).all()
    for taken_seat in taken_seats:
        available_seats[taken_seat.seat_number] = False
    session["matatu_queue_entry_id"] = matatu_queue_entry_id

    return render_template("pick_a_seat.html", available_seats=available_seats, range=range,
                           seat_numbers=seat_numbers, zip=zip)


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
        route_price_services_to_destination.append(route_price_service)
        link_list.append(base_link+str(route_price_service.id))
        if route_price_service.matatu_queue_entry:
            print(route_price_service.matatu_queue_entry)
            matatu_available_list.append(True)
        else:
            matatu_available_list.append(False)
    from_locations = []
    to_locations = []
    for route_price in route_price_services_to_destination:
        from_location = Location.query.filter_by(id=route_price.route.from_town_id).first()
        from_locations.append(from_location)
        to_location = Location.query.filter_by(id=route_price.route.to_town_id).first()
        to_locations.append(to_location)
    return render_template("list_routes.html", route_price_services=route_price_services_to_destination,
                           link_list=link_list, zip=zip, matatu_available_list=matatu_available_list,
                           from_locations=from_locations, to_locations=to_locations)


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


@app.route("/history")
@login_required
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
    from_locations =[]
    to_locations = []
    for ticket in tickets:
        route = Route.query.filter_by(number=ticket.route).first()
        from_location = Location.query.filter_by(id=route.from_town_id).first()
        to_location = Location.query.filter_by(id=route.to_town_id).first()
        from_locations.append(from_location)
        to_locations.append(to_location)

    return render_template("history.html", tickets=tickets, from_locations=from_locations, to_locations=to_locations,
                           zip=zip)


@app.route("/dissapointment/<message>")
@login_required
def dissapointment(message):
    return render_template("dissapointment.html", message=message)


@app.route("/select_matatu", methods=["POST", "GET"])
@login_required
def select_matatu():
    #look in db for routes that have this to and from
    #get all town id
    print("departure"+str(session["departure"]))
    print("to location"+str(session["destination"]))
    depart_locations = Location.query.filter_by(town=session["departure"]).all()
    destination_locations = Location.query.filter_by(town=session["destination"]).all()
    print(depart_locations)
    print(destination_locations)
    routes =[]
    for depart_location, destination_location in zip(depart_locations, destination_locations):
        routes.extend(Route.query.filter_by(from_town_id=depart_location.id).filter_by(
            to_town_id=destination_location.id).all())
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


@app.route("/book", methods=["POST", "GET"])
@login_required
def book():
    locations = Location.query.all()
    choices = [(str(location.town), str(location.town)) for location in
               locations ]
    choices = list(set(choices))
    BookSeatForm.departure = SelectField(
        'departure',
        choices=choices,
        validators=[validators.DataRequired()]
    )
    BookSeatForm.destination = SelectField(
        'destination',
        choices=choices,
        validators=[validators.DataRequired()]
    )
    form = BookSeatForm(request.form)
    if request.method == "GET":
        return render_template("book.html", form=form)
    elif request.method == "POST" and form.validate():
        destination = form.destination.data
        departure = form.departure.data
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


@app.route("/register_traveler", methods=["POST", "GET"])
def register_traveler():
    form = TravelerRegistrationForm(request.form)
    if request.method == "GET":
        #print("\n\n\nplease work\n\n")
        return render_template("register.html", form=form)
    elif request.method == 'POST' and form.validate():
        #print("\n\n\nplease work\n\n")
        id_num = form.id.data
        email = form.email.data
        pw1 = form.password.data
        pw2 = form.password2.data
        birthday = form.birthday.data
        first_name = form.first_name.data
        middle_name = form.middle_name.data
        last_name = form.last_name.data
        phone = form.phone.data

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
        traveler = Traveler(id_num, birthday, password, first_name, middle_name, last_name, salt, email, phone)
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

