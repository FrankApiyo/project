from app import app, db, Ticket, Matatu, Traveler, Location, Route, Service, Driver, Exec, Log, Event
from faker import Faker
from passwordHelper import get_salt
from passwordHelper import get_hash

import random
import pytest

fake = Faker()


def fake_password():
    return get_hash(get_salt()+fake.password())


def fake_position():
    postions = ["ceo", "coo", "cfo", "cst", "cocs"]
    return postions[random.randint()]


def fake_id():
    "".join(fake.ssn().split("-"))


@pytest.fixture(scope="module")
def tear_down_after():
    yield
    db.session.rollback()

def test_database():
    #create 10 services
    services = []
    for i in range(10):
        service = Service(fake.company())
        services.append(service)
        db.session.add(service)

    #for each service create 5 execs
    for service in services:
        for i in range(5):
            exec = Exec(fake.username(), fake_id, fake.date_of_birth(), None, fake_position(), fake_password(),
                     fake.fist_name(), fake.middle_name(), fake.last_name(), get_salt(), fake.email())
            service.execs.append(exec)
            db.session.add(exec)

    #for each service create 20 drivers
    for service in services:
        for i in range(20):
            driver = Driver(fake.username(), fake_id(), fake.matatu_service(), fake_password(), fake.first_name(),
                       fake.middle_name(), fake.last_name(), get_salt())
            service.drivers.append(driver)
            db.session.add(service)

    #create 100 locations
    locations = []
    for i in range(100):
        location = Location(fake.city(), fake.latitude(), fake.longitude())
        locations.append(location)
        db.session.add(location)

    #generate 20 fake routes for each service
    #first generate 20 unique route numbers
    route_numbers = random.sample(range(10, 1000), 20)
    for service in services:
        for i in range(20):
            route = Route(route_numbers[i], locations[random.randint(0, 99)], locations[random.randint(0, 99)])
            service.routes.append(route)
            db.session.add(route)

    #generate 20 fake matatus for each service
    for service in services:
        for i in range(20):
            matatu = Matatu(fake.license_plate, service.name, 14)
            service.matatus.append(matatu)
            db.session.add(matatu)

    #generate 100 fake travelers
    travelers = []
    for i in range(100):
        traveler = Traveler(fake.user_name(), fake_id(), fake.date_of_birth(), fake_password(), fake.first_name(),
                     fake.middle_name(), fake.last_name, get_salt(), fake.email())
        travelers.append(
            traveler
        )
        db.session.add(traveler)


    #generate 100 fake tickets
    tickets = []
    for i in range(100):
        ticket = Ticket(travelers[random.randint(0, 99)],
                        services[random.randint(0, 19)].matatus[random.randint(0, 99)],
                        fake.latitude(),
                        fake.longitude(), services[random.randint(0, 19)].drivers[random.randint(0, 99)],
                        random.randint(50, 1000), fake.date_time(),
                        services[random.randint(0, 19)].routes[random.randint(0, 20)])
        tickets.append(ticket)
        db.session.add(ticket)


    db.session.save()


def test_services():
    services = Service.query.all()
    assert len(services) == 10
