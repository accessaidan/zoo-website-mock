from flask import Flask, render_template, Blueprint
from flask_login import LoginManager, login_user
from flask import flash, redirect, url_for

from forms import RegistrationForm, LoginForm
from database import User, db

login_manager = LoginManager()

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
            return render_template('register.html', form=form)
        new_user = User(
            email=form.email.data,
            password=form.password.data,
            send_email=form.send_email.data
        )
        db.session.add(new_user)
        db.session.commit()
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
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html', form=form)