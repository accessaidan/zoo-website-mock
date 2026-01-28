
#from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()



class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    send_email = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.user_id)


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(50), db.ForeignKey('hotel_bookings.booking_id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.ticket_id'), nullable=False)
    payment_id = db.Column(db.String(50), db.ForeignKey('payments.payment_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class tickets(db.Model):
    ticket_id = db.Column(db.Integer, primary_key=True)
    children = db.Column(db.Float, nullable=False)
    adults = db.Column(db.Float, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(50), nullable=False)
    child_price = db.Column(db.Float, nullable=False)
    adult_price = db.Column(db.Float, nullable=False)

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
    number = db.Column(db.Integer, unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)



def populate_rooms():
    if rooms.query.first() is None:
        room101 = rooms(number=101, type='Budget', capacity=4, price_per_night=50.0)
        room102 = rooms(number=102, type='Budget', capacity=4, price_per_night=50.0)
        room103 = rooms(number=103, type='Budget', capacity=2, price_per_night=30.0)
        room201 = rooms(number=201, type='Standard', capacity=4, price_per_night=80.0)
        room202 = rooms(number=202, type='Standard', capacity=4, price_per_night=80.0)
        room203 = rooms(number=203, type='Standard', capacity=2, price_per_night=50.0)
        room301 = rooms(number=301, type='Deluxe', capacity=4, price_per_night=120.0)
        room302 = rooms(number=302, type='Deluxe', capacity=4, price_per_night=120.0)
        room303 = rooms(number=303, type='Deluxe', capacity=2, price_per_night=90.0)
        db.session.add_all([room101, room102, room103, room201, room202, room203, room301, room302, room303])
        db.session.commit()

def get_available_rooms(check_in_date, check_out_date, visitors):
    booked_room_ids = db.session.query(hotel_bookings.room_id).filter(
        hotel_bookings.check_in_date < check_out_date,
        hotel_bookings.check_out_date > check_in_date
    ).subquery()

    available_rooms = rooms.query.filter(
        rooms.availability == True,
        rooms.capacity >= visitors,
        ~rooms.room_id.in_(booked_room_ids)
    ).all()

    return available_rooms

def make_admins():
    if User.query.filter_by(is_admin=True).first() is None:
        admin_user = User(email='admin@example.com', password='admin', is_admin=True)
        db.session.add(admin_user)

    db.session.commit()