from flask import Flask, render_template, Blueprint
from flask import flash, redirect, url_for
from flask_bootstrap import Bootstrap5

from database import User, db


app = Flask(__name__)
app.secret_key = 'secret_key'
Bootstrap5(app)


# print(app.jinja_env.globals)  # <--- check if 'bootstrap5' exists

from routes import routes_blueprint

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


db.init_app(app)







with app.app_context():
    db.create_all()

app.register_blueprint(routes_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

