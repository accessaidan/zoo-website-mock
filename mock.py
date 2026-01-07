from flask import Flask, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import flash, redirect, url_for

from routes import routes_blueprint
from database import User, db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


db.init_app(app)


with app.app_context():
    db.create_all()


app.register_blueprint(routes_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

