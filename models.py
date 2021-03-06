from app import db

drivers = db.Table('service_drivers',
    db.Column('service', db.Text(), db.ForeignKey('service.name')),
    db.Column('driver', db.Text(), db.ForeignKey('driver.id'))
    )

execs = db.Table('service_exec',
    db.Column('service', db.Text(), db.ForeignKey('service.name')),
    db.Column('exec', db.Text(), db.ForeignKey('exec.id'))
    )

matatu_routes = db.Table("matatu_routes",
                         db.Column('matatu_registration', db.Text(), db.ForeignKey('matatu.registration')),
                         db.Column('route_number', db.Integer(), db.ForeignKey('route.number'))
                         )

locations = db.Table('service_location',
    db.Column('service', db.Text(), db.ForeignKey('service.name')),
    db.Column('location', db.Integer(), db.ForeignKey('location.id'))
    )

location_on_route = db.Table("location_on_route",
    db.Column('location', db.Integer(), db.ForeignKey('location.id')),
    db.Column('route', db.Integer(), db.ForeignKey('route.number'))
    )


class TakenSeatInstance(db.Model):
    __tablename__ = "taken_seats"
    __table_args__ = (
        db.UniqueConstraint('matatu_queue_instance_id', 'seat_number', name='unique_component_commit'),
    )
    id = db.Column(db.Integer, primary_key=True)
    matatu_queue_instance_id = db.Column(db.Integer, db.ForeignKey("matatu_queue.id"), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)

    def __init__(self, seat_number):
        self.seat_number = seat_number

    def __repr__(self):
        return "\nSeat no: '{}' in matatu registration : '{}'\n".format(self.seat_number,
                                                                        self.matatu_queue_instance.matatu.registration)


class MatatuQueueInstance(db.Model):
    #TODO remember that matatu queue entries are remmoved from the matatu que once they are full that is no of seats
    # gets to zero and also remove all the tacken seatInstances from the TackenSeats table
    __tablename__ = "matatu_queue"
    id = db.Column(db.Integer(), primary_key=True)
    no_of_vacant_seats = db.Column(db.Integer(), default=0, nullable=False)
    route_price_service_id = db.Column(db.Integer(), db.ForeignKey("route_price_service.id"), nullable=False)
    matatu_registration = db.Column(db.Text(), db.ForeignKey("matatu.registration"), nullable=False, unique=True)
    taken_seats = db.relationship(
        'TakenSeatInstance',
        backref='matatu_queue_instance',
        lazy='dynamic'
    )

    def __init__(self, no_of_vacant_seats):
        self.no_of_vacant_seats = no_of_vacant_seats

    def __repr__(self):
        return "\nMatatuQueueEntry\n"


class RoutePriceService(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    service_name = db.Column(db.Text(), db.ForeignKey('service.name'))
    route_number = db.Column(db.Integer(), db.ForeignKey('route.number'))
    price = db.Column(db.Float(), nullable=False)
    matatu_queue_entry = db.relationship('MatatuQueueInstance', backref='route_price_service', uselist=False)


    def __init__(self, price):
        self.price = price

    def __repr__(self):
        return "\nService: '{}'\nroute: '{}'\nprice: '{}'\n".format(self.service, self.route, self.price)


class Location(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    #description of location, eg. nakuru,odion or Nairobi, afya center
    town = db.Column(db.Text(), nullable=False)
    specific_location = db.Column(db.Text(), nullable=False)
    lat = db.Column(db.Float(), db.CheckConstraint("lat >= -90 and lat <= 90"), nullable=False)
    lng = db.Column(db.Float(), db.CheckConstraint("lng >= -180 and lng <= 180"), nullable=False)
    #we can't have 2 locations of the same latitude and longitude
    __table_args__ = (
        db.UniqueConstraint('lng', 'lat'),
    )



    def __init__(self, town, specific_location, lat, lng):
        self.town = town
        self.lat = lat
        self.lng =lng
        self.specific_location = specific_location

    def __repr__(self):
        return "\ntown: '{}'\nlocation: '{}'\n".format(self.town, self.specific_location)


class Route(db.Model):
    number = db.Column(db.Integer(), primary_key=True)
    from_town_id = db.Column(db.Integer, db.ForeignKey("location.id"), primary_key=False)
    to_town_id = db.Column(db.Integer, db.ForeignKey("location.id"), primary_key=False)
    route_prices = db.relationship(
        "RoutePriceService",
        backref='route',
        lazy='dynamic'
    )

    def __init__(self, number, from_location, to_location):
        self.number = number
        self.from_town_id = from_location
        self.to_town_id = to_location

    def __repr__(self):
        return "\nRoute: number'{}'\nto_town: '{}'\nfrom_town: '{}'".format(self.number, self.to_town_id,
                                                                                    self.from_town_id)


class Person:
    id = db.Column(db.Text(), primary_key=True)
    birthday = db.Column(db.DateTime())
    password = db.Column(db.Text(), nullable=False)
    first_name = db.Column(db.Text(), nullable=False)
    middle_name = db.Column(db.Text(), nullable=True)
    last_name = db.Column(db.Text(), nullable=False)
    salt = db.Column(db.Text(), nullable=False)
    email = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.Text(), nullable=False)

class Driver(db.Model, Person):
    matatu = db.relationship('Matatu', backref='driver', uselist=False)

    def __init__(self, id, birthday, password, first_name, middle_name, last_name, salt,
                 email, phone):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.salt = salt
        self.id = id
        self.birthday = birthday
        self.phone = phone

    def __repr__(self):
        return "\nDriver name'{}'\nid '{}'\n".format(self.middle_name, self.id)

class Service(db.Model):
    name = db.Column(db.Text(), primary_key=True)
    #logo will be added later on after database is ensured to be working
    route_prices = db.relationship(
        "RoutePriceService",
        backref='service',
        lazy='dynamic'
    )
    drivers = db.relationship(
        'Driver',
        secondary=drivers,
        backref=db.backref('services', lazy='dynamic')
        )
    locations = db.relationship(
        'Location',
        secondary=locations,
        backref=db.backref('services', lazy='dynamic')
    )
    execs = db.relationship(
        'Exec',
        secondary=execs,
        backref=db.backref('services', lazy='dynamic')
        )
    matatus = db.relationship(
        'Matatu',
        backref='service',
        lazy='dynamic'
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        #add ceo and name here
        return "\nMatatu Service: '{}'\n".format(self.name)


class Matatu(db.Model):
    registration = db.Column(db.Text(), primary_key=True)
    matatu_service = db.Column(db.Text(), db.ForeignKey('service.name'), nullable=False)
    seats = db.Column(db.Integer())
    driver_id = db.Column(db.Text(), db.ForeignKey("driver.id"), nullable=True)

    routes = db.relationship(
        'Route',
        secondary=matatu_routes,
        backref=db.backref('matatus', lazy='dynamic')
    )
    matatu_queue_entry = db.relationship('MatatuQueueInstance', backref='matatu', uselist=False)

    def __init__(self, registration, seats):
        self.seats = seats
        self.registration = registration

    def __repr__(self):
        return "\n<Matatu registration:'{}', service: '{}'>\n".format(self.registration, self.matatu_service)


class Ticket(db.Model):
    #TODO add seat number here
    #TODO add fulfilled and payed fields to be updated later
    id = db.Column(db.Integer(), primary_key=True)
    traveler = db.Column(db.Text(), db.ForeignKey("traveler.id"), nullable=False)
    matatu = db.Column(db.Text(), db.ForeignKey("matatu.registration"), nullable=False)
    pick_up_lat = db.Column(db.Float(), db.CheckConstraint("pick_up_lat >= -90 and pick_up_lat <= 90"), nullable=False)
    pick_up_lng = db.Column(db.Float(), db.CheckConstraint("pick_up_lng >= 0 and pick_up_lng <= 180"), nullable=False)
    driver = db.Column(db.Text(), db.ForeignKey("driver.id"), nullable=True)
    cost = db.Column(db.Float(), nullable=False)
    route = db.Column(db.Integer(), db.ForeignKey("route.number"), nullable=False)
    fulfilled = db.Column(db.Boolean, nullable=False, default=False)
    payed = db.Column(db.Boolean, nullable=False, default=False)
    balance = db.Column(db.Float(), nullable=False)


    def __init__(self, traveler, matatu, pick_up_lat, pick_up_lng, driver, cost, route):
        self.traveler = traveler
        self.matatu = matatu
        self.pick_up_lat = pick_up_lat
        self.pick_up_lng = pick_up_lng
        self.driver = driver
        self.cost = cost
        self.route = route

    def __repr__(self):
        return "\Ticker no: {}".format(self.id)


class Exec(db.Model, Person):
    position = db.Column(db.Text(), nullable=True)

    def __init__(self, birthday, position, password, first_name, middle_name, last_name,
                 salt, email, id, phone):
        self.email = email
        self.password = password
        self.id = id
        self.birthday = birthday
        self.position = position
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.salt = salt
        self.phone = phone

    def __repr__(self):
        return "\nExec name'{}'\nposition '{}'\nid '{}'\nmatatu_service: '{}'\n".format(self.middle_name,
                                                                                        self.position, self.id,
                                                                                        self.services)


class Traveler(Person, db.Model):
    outstanding = db.Column(db.Float, default=0)
    def __init__(self, id, birthday, password, first_name, middle_name, last_name, salt, email, phone):
        self.password = password
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.id = id
        self.birthday = birthday
        self.salt = salt
        self.email = email
        self.phone = phone

    def __repr__(self):
        return "\nTraveler name'{}'\nid '{}'\n".format(self.middle_name, self.id)

class DriverPicture(db.Model):
    #files will be saved using this id i.e: your-image-path/(ID).(ext)
    id = db.Column(db.Integer(), primary_key=True)
    #for some reason we need to keep track of original name of file and extention
    original_name = db.Column(db.Text(), nullable=False)
    extension = db.Column(db.Text(), nullable=False)
    #we also need to keep track of when the file was uploaded
    datetime = db.Column(db.DateTime(), nullable=False)
    #we are missing unique because we can keep several images  of the same driver
    driver = db.Column(db.Text(), db.ForeignKey("driver.id"), nullable=False)


    def __init__(self, id, original_name, extention, datetime, driver):
        self.id = id
        self.original_name = original_name
        self.extension = extention
        self.datetime = datetime
        self.driver = driver

    def __repr__(self):
        return "\nDriver picture id: {}\n".format(self.id)


class Log(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    datetime = db.Column(db.DateTime(), nullable=False)
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

