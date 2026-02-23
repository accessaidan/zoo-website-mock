#from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    send_email = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.user_id)


class tickets(db.Model):
    ticket_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    children = db.Column(db.Integer, nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    seniors = db.Column(db.Integer, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    child_price = db.Column(db.Float, nullable=False)
    adult_price = db.Column(db.Float, nullable=False)
    senior_price = db.Column(db.Float, nullable=False)
    # No custom __init__ method!

class payments(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(20), nullable=False)
    card_holder_name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.String(10), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('hotel_bookings.booking_id'), nullable=False)

class hotel_bookings(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    room_number = db.Column(db.String(50), nullable=False)
    booking_date = db.Column(db.String, nullable=False)
    check_in_date = db.Column(db.String, nullable=False)
    check_out_date = db.Column(db.String, nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    needs = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)

class rooms(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)

class ticket_prices(db.Model):
    price_id = db.Column(db.Integer, primary_key=True)
    child_price = db.Column(db.Float, nullable=False)
    adult_price = db.Column(db.Float, nullable=False)
    senior_price = db.Column(db.Float, nullable=False)


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
    ).all()
    
    booked_room_ids = [room_id for (room_id,) in booked_room_ids]

    if booked_room_ids:
        available_rooms = rooms.query.filter(
            rooms.capacity >= visitors,
            ~rooms.room_id.in_(booked_room_ids)
        ).all()

    else:
        available_rooms = rooms.query.filter(
            rooms.capacity >= visitors
        ).all()
    return available_rooms

def can_block_room(room_number, blocked_from, blocked_to):
    overlapping_booking = hotel_bookings.query.filter(
        hotel_bookings.room_number == room_number,
        hotel_bookings.check_in_date < blocked_to,
        hotel_bookings.check_out_date > blocked_from
    ).first()
    return overlapping_booking is None

def make_admins():
    if User.query.filter_by(is_admin=True).first() is None:
        admin_user = User(email='admin@example.com', password=Bcrypt().generate_password_hash('admin').decode('utf-8'), is_admin=True)
        db.session.add(admin_user)

    db.session.commit()

def populate_ticket_prices():
    if ticket_prices.query.first() is None:
        default_prices = ticket_prices(
            child_price=10.0,
            adult_price=20.0,
            senior_price=15.0
        )
        db.session.add(default_prices)
        db.session.commit()
