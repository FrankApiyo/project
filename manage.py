from app import app, db, Ticket, Matatu, Traveler, Location, Route, Service, Driver, Exec, Log, Event, \
    RoutePriceService, MatatuQueueInstance, TakenSeatInstance


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Ticket=Ticket, Matatu=Matatu, Traveler=Traveler, Location=Location, Route=Route,
                Service=Service, Driver=Driver, Exec=Exec, Log=Log, Event=Event, RoutePriceService=RoutePriceService,
                MatatuQueueInstance=MatatuQueueInstance, TakenSeatInstance=TakenSeatInstance)