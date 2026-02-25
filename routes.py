from flask import Flask, render_template, Blueprint, request, session
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask import flash, redirect, url_for
import datetime
from datetime import date
from flask_bcrypt import Bcrypt
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView


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

        hashed_password = Bcrypt().generate_password_hash(form.password.data).decode('utf-8')


        new_user = User(
            email=form.email.data,
            password=hashed_password,
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
        if user and Bcrypt().check_password_hash(user.password, form.password.data):
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
    if request.method == 'POST':
        try:
            check_in_date = datetime.datetime.strptime(form.check_in_date.data, '%Y-%m-%d').date()
            check_out_date = datetime.datetime.strptime(form.check_out_date.data, '%Y-%m-%d').date()
        
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return render_template('Roomsearch.html', form=form)
        adults = int(form.adults.data)
        children = int(form.children.data)
        needs = form.needs.data

        if check_in_date >= check_out_date:
            flash('Check-out date must be after check-in date.', 'error')
            return render_template('Roomsearch.html', form=form)
        
        if check_in_date < date.today():
            flash('Check-in date cannot be in the past.', 'error')
            return render_template('Roomsearch.html', form=form)
        
        if adults < 1:
            flash('At least one adult must be included in the booking.', 'error')
            return render_template('Roomsearch.html', form=form)
        
        if adults + children > 4:
            flash('The maximum number of guests per room is 4.', 'error')
            return render_template('Roomsearch.html', form=form)
        
        if needs and len(needs) > 200:
            flash('Special needs/requests must be 200 characters or fewer.', 'error')
            return render_template('Roomsearch.html', form=form)
        
        if check_in_date > date.today() + datetime.timedelta(days=365):
            flash('Check-in date cannot be more than one year in the future.', 'error')
            return render_template('Roomsearch.html', form=form)
        
        if check_out_date - check_in_date > datetime.timedelta(days=14):
            flash('The maximum stay is 14 days.', 'error')
            return render_template('Roomsearch.html', form=form)
        

        available_rooms = get_available_rooms(check_in_date, check_out_date, adults + children)

        if not available_rooms:
            flash('No rooms available for the selected dates and number of guests.', 'error')
            return render_template('Roomsearch.html', form=form)
        

        return render_template('available_rooms.html', rooms=available_rooms, check_in_date=check_in_date, check_out_date=check_out_date, adults=adults, children=children, needs=needs)

    return render_template('Roomsearch.html', form=form)

@routes_blueprint.route('/book_room/<int:room_id>', methods=['POST'])
def book_room(room_id):
    room_num = rooms.query.get(room_id).number
    booking_date = date.today()
    check_in_date = datetime.datetime.strptime(request.form.get('check_in_date'), '%Y-%m-%d').date()
    check_out_date = datetime.datetime.strptime(request.form.get('check_out_date'), '%Y-%m-%d').date()
    adults = int(request.form.get('adults'))
    children = int(request.form.get('children'))
    needs = request.form.get('needs')
    price = rooms.query.get(room_id).price_per_night * (check_out_date - check_in_date).days

    session['booking_details'] = {
        'room_id': room_id,
        'room_num': room_num,
        'booking_date': booking_date.strftime('%Y-%m-%d'),
        'check_in_date': check_in_date.strftime('%Y-%m-%d'),
        'check_out_date': check_out_date.strftime('%Y-%m-%d'),
        'adults': adults,
        'children': children,
        'needs': needs,
        'price': price
        
    }
    return redirect(url_for('routes.room_payment', booking_details=session['booking_details']))

@routes_blueprint.route('/payment', methods=['GET', 'POST'])
@login_required
def room_payment():
    form = PaymentForm()
    if form.validate_on_submit():
        flash('Payment successful! Your booking is confirmed.', 'success')


        new_booking = hotel_bookings(
            user_id=current_user.user_id,
            room_id=session['booking_details']['room_id'],
            room_number=session['booking_details']['room_num'],
            booking_date=session['booking_details']['booking_date'],
            check_in_date=session['booking_details']['check_in_date'],
            check_out_date=session['booking_details']['check_out_date'],
            adults=session['booking_details']['adults'],
            children=session['booking_details']['children'],
            needs=session['booking_details']['needs'],
            price=session['booking_details']['price']
        )
        db.session.add(new_booking)
        db.session.commit()


        card_number = form.card_number.data
        card_holder_name = form.full_name.data
        expiry_date = form.expiry_date.data
        
        hashed_card_number = Bcrypt().generate_password_hash(card_number).decode('utf-8')
        hashed_card_holder_name = Bcrypt().generate_password_hash(card_holder_name).decode('utf-8')
        hashed_expiry_date = Bcrypt().generate_password_hash(expiry_date).decode('utf-8')


        new_payment = payments(
            card_number=hashed_card_number,
            card_holder_name=hashed_card_holder_name,
            expiry_date=hashed_expiry_date,
            booking_id=new_booking.booking_id
        )

        db.session.add(new_payment)
        db.session.commit()

        session.pop('booking_details', None)

        return redirect(url_for('routes.index'))
    return render_template('room_payment.html', form=form, booking_details=session.get('booking_details'))

@routes_blueprint.route('/tickets', methods=['GET', 'POST'])
@login_required
def tickets_booking():
    form = TicketPurchaseForm()
    if form.validate_on_submit():
        children = int(form.children.data)
        adults = int(form.adults.data)
        seniors = int(form.seniors.data)


        print(children, adults, seniors)
        # Calculate total price based on ticket prices
        child_price = ticket_prices.query.first().child_price
        adult_price = ticket_prices.query.first().adult_price
        senior_price = ticket_prices.query.first().senior_price
        total_price = (children * child_price) + (adults * adult_price) + (seniors * senior_price)

        session['ticket_details'] = {
            'children': children,
            'adults': adults,
            'seniors': seniors,
            'total_price': total_price
        }

        print("Ticket details stored in session:")
        print(session['ticket_details'])

        return redirect(url_for('routes.ticket_payment', ticket_details=session['ticket_details']))

    return render_template('book_tickets.html', form=form)

@routes_blueprint.route('/ticket_payment', methods=['GET', 'POST'])
@login_required
def ticket_payment():
    form = PaymentForm()
    if form.validate_on_submit():
        flash('Payment successful! Your tickets are confirmed.', 'success')

        new_ticket = tickets(
            user_id=current_user.user_id,
            children=session['ticket_details']['children'],
            adults=session['ticket_details']['adults'],
            seniors=session['ticket_details']['seniors'],
            child_price=ticket_prices.query.first().child_price,
            adult_price=ticket_prices.query.first().adult_price,
            senior_price=ticket_prices.query.first().senior_price
        )


        db.session.add(new_ticket)
        db.session.commit()
        flash('Tickets purchased successfully!', 'success')

        card_number = form.card_number.data
        card_holder_name = form.full_name.data
        expiry_date = form.expiry_date.data

        hashed_card_number = Bcrypt().generate_password_hash(card_number).decode('utf-8')
        hashed_card_holder_name = Bcrypt().generate_password_hash(card_holder_name).decode('utf-8')
        hashed_expiry_date = Bcrypt().generate_password_hash(expiry_date).decode('utf-8')

        new_payment = payments(
            card_number=hashed_card_number,
            card_holder_name=hashed_card_holder_name,
            expiry_date=hashed_expiry_date,
            ticket_id=new_ticket.ticket_id
        )

        db.session.add(new_payment)
        db.session.commit()

        session.pop('ticket_details', None)

        return redirect(url_for('routes.index'))
    return render_template('tickets_payment.html', form=form, ticket_details=session.get('ticket_details'))


@routes_blueprint.route('/account')
@login_required
def account():
    email = current_user.email
    user_bookings = hotel_bookings.query.filter_by(user_id=current_user.user_id).all()
    user_tickets = tickets.query.filter_by(user_id=current_user.user_id).all()
    return render_template('account.html', bookings=user_bookings, email=email, tickets=user_tickets)

@routes_blueprint.route('/cancel_booking', methods=['POST'])
@login_required
def cancel_booking():
    booking_id = request.form.get('booking_id')
    booking = hotel_bookings.query.get(booking_id)
    payment = payments.query.filter_by(booking_id=booking_id).first()
    if booking and payment:
        db.session.delete(booking)
        db.session.delete(payment)
        db.session.commit()
        flash('Booking cancelled successfully.', 'success')
    else:
        flash('Booking not found.', 'error')

    return redirect(url_for('routes.account'))

@routes_blueprint.route('/cancel_ticket', methods=['POST'])
@login_required
def cancel_ticket():
    ticket_id = request.form.get('ticket_id')
    ticket = tickets.query.get(ticket_id)
    payment = payments.query.filter_by(ticket_id=ticket_id).first()
    if ticket:
        db.session.delete(ticket)
        db.session.delete(payment)

        db.session.commit()
        flash('Ticket cancelled successfully.', 'success')
    else:
        flash('Ticket not found.', 'error')

    return redirect(url_for('routes.account'))

@routes_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('routes.index'))

@routes_blueprint.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if booking := hotel_bookings.query.filter_by(user_id=current_user.user_id).first():
        flash('Please cancel all your bookings before deleting your account.', 'error')
        return redirect(url_for('routes.account'))

    else:
        user = current_user
        db.session.delete(user)
        db.session.commit()
        flash('Account deleted successfully.', 'success')
        return redirect(url_for('routes.index'))

@routes_blueprint.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('routes.index'))
    return render_template('admin_panel.html')

@routes_blueprint.route('/create_admin_user', methods=['POST', 'GET'])
@login_required
def create_admin_user():
    if not current_user.is_admin:
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('routes.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('routes.register_admin'))

        hashed_password = Bcrypt().generate_password_hash(form.password.data).decode('utf-8')

        new_user = User(
            email=form.email.data,
            password=hashed_password,
            send_email=form.send_email.data,
            is_admin=True
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Admin user created successfully!')
        return redirect(url_for('routes.admin_panel'))
    return render_template('register_admin.html', form=form)

@routes_blueprint.route('/room_availability')
@login_required
def room_availability():
    if not current_user.is_admin:
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('routes.index'))
    form = EditAvailabilityForm()
    return render_template('room_availability.html', form=form)

@routes_blueprint.route('/edit_room_availability', methods=['POST', 'GET'])
@login_required
def edit_room_availability():
    if not current_user.is_admin:
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('routes.index'))

    
    form = EditAvailabilityForm()
    if form.validate_on_submit():
        print("Form data received:")
        # Process the form data
        room_number = form.room_number.data
        blocked_from = form.blocked_from.data
        blocked_to = form.blocked_to.data

        try:
            blocked_from = datetime.datetime.strptime(form.blocked_from.data, '%Y-%m-%d').date()
            blocked_to = datetime.datetime.strptime(form.blocked_to.data, '%Y-%m-%d').date()

        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return render_template('room_availability.html', form=form)

        if blocked_from >= blocked_to:
            flash('Blocked to date must be after blocked from date.', 'error')
            return render_template('room_availability.html', form=form)

        if blocked_from < date.today():
            flash('Blocked from date cannot be in the past.', 'error')
            return render_template('room_availability.html', form=form)

        if not can_block_room(room_number, blocked_from, blocked_to):
            flash('Room is already booked for the selected dates.', 'error')
            return render_template('room_availability.html', form=form)

        room = rooms.query.filter_by(number=room_number).first()
        if not room:
            flash('Room not found.', 'error')
            return render_template('room_availability.html', form=form)
        
        new_block = hotel_bookings(
            user_id=current_user.user_id,
            room_id=room.id,
            room_number=room.number,
            booking_date=datetime.datetime.now(),
            check_in_date=blocked_from,
            check_out_date=blocked_to,
            adults=1,
            children=0,
            needs='',
            price=0
        )

        db.session.add(new_block)
        db.session.commit()

        flash(f'Room {room_number} blocked from {blocked_from} to {blocked_to}.', 'success')


    return render_template('room_availability.html', form=form)
