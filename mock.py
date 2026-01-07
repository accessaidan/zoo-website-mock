from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db' 
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    send_email = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(50), db.ForeignKey('hotel_bookings.booking_id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.ticket_id'), nullable=False)
    payment_id = db.Column(db.String(50), db.ForeignKey('payments.payment_id'), nullable=False)

class tickets(db.Model):
    ticket_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(50), nullable=False)

class payments(db.Model):
    payment_id = db.Column(db.String(50), primary_key=True)
    card_number = db.Column(db.String(20), nullable=False)
    card_holder_name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.String(10), nullable=False)
    save_card = db.Column(db.Boolean, default=False)

class hotel_bookings(db.Model):
    booking_id = db.Column(db.String(50), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    needs = db.Column(db.String(200), nullable=True)

class rooms(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.calendar_id'), nullable=False)

class calendars(db.Model):
    calendar_id = db.Column(db.Integer, primary_key=True)
    availability = db.Column(db.String(200), nullable=False) 

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)