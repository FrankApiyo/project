from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DevConfig
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    traveller = db.Column(db.Text(), db.ForeignKey("traveller.id"), nullable=False)
    matatu = db.Column(db.Text(), db.ForeignKey("matatu.registration"), nullable=False)
    pick_up_lat = db.Column(db.Float(), db.CheckConstraint("pick_up_lat >= -90 and pick_up_lat <= 90"), nullable=False)
    pick_up_lng = db.Column(db.Float(), db.CheckConstraint("pick_up_lng >= 0 and pick_up_lng <= 180"), nullable=False)
    driver = db.Column(db.Text(), db.ForeignKey("driver.id"), nullable=False)
    cost = db.Column(db.Float(), nullable=False)
    pick_up_time = db.Column(db.DateTime(), nullable=False)
    route = db.Column(db.Integer(), db.ForeignKey("route.number"), nullable=False)

    def __init__(self, traveller, matatu, pick_up_lat, pick_up_lng, driver, cost, pick_up_time, route):
        self.traveller = traveller
        self.matatu = matatu
        self.pick_up_lat = pick_up_lat
        self.pick_up_lng = pick_up_lng
        self.driver = driver
        self.cost = cost
        self.pick_up_time = pick_up_time
        self.route = route

    def __repr__(self):
        return "\Ticker no: {}".format(self.id)


class Person():
    name = db.Column(db.Text(), nullable=False)
    id = db.Column(db.Text(), primary_key=True)
    age = db.Column(db.Integer(), default=18)


class ServiceEmployee(Person):
    #why this is nullable is beause an employee can leave a service but we still would like to retain data about them
    matatu_service = db.Column(db.Text(), nullable=True)


class Exec(ServiceEmployee, db.Model):
    position = db.Column(db.Text(), nullable=True)
    matatu_service = db.Column(db.Text(), nullable=False)

    def __init__(self, name, id, age, matatu_service, position):
        self.name = name
        self.id = id
        self.age = age
        self.matatu_service = matatu_service
        self.position = position

    def __repr__(self):
        return "\nExec name'{}'\nposition '{}'\nid '{}'\nage '{}'\nmatatu_service: '{}'\n".format(self.name, self.position, self.id, self.age, self.matatu_service)


class Traveller(Person, db.Model):
    def __init__(self, name, id, age):
        self.name = name
        self.id = id
        self.age = age
    def __repr__(self):
        return "\nTraveller name'{}'\nid '{}'\nage '{}'\n".format(self.name, self.id, self.age)


class Driver(ServiceEmployee, db.Model):
    def __init__(self, name, id, age, matatu_service):
        self.name = name
        self.id = id
        self.age = age
        self.matatu_service = matatu_service

    def __repr__(self):
        return "\nDriver name'{}'\nid '{}'\nage '{}'\nmatatu_service: '{}'\n".format(self.name, self.id, self.age, self.matatu_service)


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