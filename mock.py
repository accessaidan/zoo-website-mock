from flask import Flask, render_template
from flask import flash, redirect, url_for


from routes import routes_blueprint
from database import User, db
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user, UserMixin



app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


app.register_blueprint(routes_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

