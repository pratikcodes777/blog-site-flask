from flask import Flask, redirect, render_template, request, url_for, flash , session, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from sqlalchemy import desc, or_
import base64
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required, UserMixin ,LoginManager
import random
from flask_mail import Mail, Message



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'hello'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'pratik.barakoti01@gmail.com'
app.config['MAIL_PASSWORD'] = 'ubvp iqhk ompc bwwe'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)


