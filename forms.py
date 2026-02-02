# from flask import render_template, Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError

# from flask import flash, redirect, url_for
# from mock import db
# from database import User
# login_manager = LoginManager()


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password should be at least 8 characters long.'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', message='Password must contain letters and numbers.')])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    send_email = BooleanField('Receive promotional emails', default=True)
    submit = SubmitField('Register')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', default=False)
    submit = SubmitField('Login')


class RoomSearch(FlaskForm):
    check_in_date = StringField('Check-in Date', validators=[DataRequired()], render_kw={"placeholder": "DD/MM/YYYY"})
    check_out_date = StringField('Check-out Date', validators=[DataRequired()], render_kw={"placeholder": "DD/MM/YYYY"})
    adults = StringField('Number of Adults', validators=[DataRequired()])
    children = StringField('Number of Children', validators=[DataRequired()])
    needs = StringField('Special Needs / Requests')
    submit = SubmitField('find rooms')

class PaymentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    expiry_date = StringField('Expiry Date (MM/YY)', validators=[DataRequired(), Regexp(r'^(0[1-9]|1[0-2])\/?([0-9]{2})$', message='Invalid expiry date format.')])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=4)])
    submit = SubmitField('Pay Now')

    def validate_card_number(self, field):
        if not field.data.isdigit():
            raise ValidationError('Card number must contain only digits.')
        # Implement Luhn algorithm check here if needed
    
