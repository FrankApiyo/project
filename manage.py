from app import app, db, Ticket, Matatu, Traveller, Location, Route, Service, Driver, Exec, Log, Event


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Ticket=Ticket, Matatu=Matatu, Traveller=Traveller, Location=Location, Route=Route,
                Service=Service, Driver=Driver, Exec=Exec, Log=Log, Event=Event)