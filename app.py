from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date

app = Flask(__name__)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airline.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flight Model
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_city = db.Column(db.String(100), nullable=False)
    to_city = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    bookings = db.relationship('Booking', backref='flight', lazy=True)  # Add relationship to bookings

# Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)  # Foreign key to flight
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

# Home/Search Flights Page
@app.route('/', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        from_city = request.form['from_city']
        to_city = request.form['to_city']
        date = request.form['date']
        flights = Flight.query.filter_by(from_city=from_city, to_city=to_city, date=date).all()
        return render_template('search_results.html', flights=flights)
    return render_template('search_flights.html')

# Book Flight Page
@app.route('/book/<int:flight_id>', methods=['GET', 'POST'])
def book_flight(flight_id):
    flight = Flight.query.get(flight_id)
    if request.method == 'POST':
        passenger_name = request.form['passenger_name']
        booking = Booking(passenger_name=passenger_name, flight_id=flight_id)
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_confirmation.html', booking=booking, flight=flight)
    return render_template('book_flight.html', flight=flight)

@app.route('/bookings')
def view_bookings():
    bookings = Booking.query.all()
    return render_template('view_bookings.html', bookings=bookings)

# Initialize the Database and Add Flights
@app.before_request
def create_tables():
    db.create_all()
    # Add sample flights to the database if they don't exist
    if not Flight.query.first():
        # Convert string dates to Python date objects
        flight1 = Flight(from_city="Mumbai", to_city="Delhi", date=date(2024, 10, 20), price=5000.0)
        flight2 = Flight(from_city="Mumbai", to_city="Bangalore", date=date(2024, 10, 22), price=4500.0)
        flight3 = Flight(from_city="Chennai", to_city="Kolkata", date=date(2024, 11, 1), price=5500.0)
        flight4 = Flight(from_city="Delhi", to_city="Hyderabad", date=date(2024, 10, 25), price=4800.0)
        
        db.session.add_all([flight1, flight2, flight3, flight4])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)