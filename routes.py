from flask import Flask, render_template, Blueprint, request
from flask_login import LoginManager, login_user, login_required, current_user
from flask import flash, redirect, url_for
import datetime
from datetime import date
import uuid


from forms import *
from database import *



routes_blueprint = Blueprint('routes', __name__)
@routes_blueprint.route('/')

def index():

    return render_template('index.html')

@routes_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('routes.register'))
        new_user = User(
            email=form.email.data,
            password=form.password.data,
            send_email=form.send_email.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('routes.login'))
    

    return render_template('register.html', form=form)

@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            login_user(user, remember=form.remember_me.data)
            flash('Login successful!', 'success')
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)

@routes_blueprint.route('/Roomsearch', methods=['GET', 'POST'])
@login_required
def Roomsearch():
    form = RoomSearch()
    if form.validate_on_submit():
        check_in_date = datetime.datetime.strptime(form.check_in_date.data, '%d/%m/%Y').date()
        check_out_date = datetime.datetime.strptime(form.check_out_date.data, '%d/%m/%Y').date()
        adults = int(form.adults.data)
        children = int(form.children.data)
        needs = form.needs.data

        available_rooms = get_available_rooms(check_in_date, check_out_date, adults + children)

        return render_template('available_rooms.html', rooms=available_rooms, check_in_date=check_in_date, check_out_date=check_out_date, adults=adults, children=children, needs=needs)

    return render_template('Roomsearch.html', form=form)

@routes_blueprint.route('/book_room', methods=['POST'])
def book_room():
    room_id = request.form.get('room_id')
    check_in_date = datetime.datetime.strptime(request.form.get('check_in_date'), '%Y-%m-%d').date()
    check_out_date = datetime.datetime.strptime(request.form.get('check_out_date'), '%Y-%m-%d').date()
    adults = int(request.form.get('adults'))
    children = int(request.form.get('children'))
    needs = request.form.get('needs')

    new_booking = hotel_bookings(
        room_id=room_id,
        booking_date=date.today(),
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        adults=adults,
        children=children,
        needs=needs
    )



    #db.session.add(new_booking)
    #db.session.commit()
    flash('Room booked successfully!', 'success')
    return redirect(url_for('routes.index'))

@routes_blueprint.route('/cart')
@login_required
def cart():

    return render_template('cart.html', )
