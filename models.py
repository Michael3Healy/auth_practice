from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from pdb import set_trace

db = SQLAlchemy()

def connect_db(app):
    db.init_app(app)

bcrypt = Bcrypt()

def create_user(form):
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    new_user = User.register(username, password, email, first_name, last_name)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def authenticate_user(form):
    username = form.username.data
    password = form.password.data
    user = User.authenticate(username, password)
    return user

def incorrect_user_logged_in(session, username):
    logged_in_username = session.get('username')
    user = User.query.filter_by(username=logged_in_username).first()
    return not (session.get('username') == username) and not (user.is_admin)

def no_user_logged_in(session):
    return not session.get('username')

def has_admin(session):
    user = User.query.filter_by(username=session.get('username')).first()

    # user var only exists if user is admin (and deleted someone else)
    if not user:
        return False
    return True 

def create_feedback(form, username):
    title = form.title.data
    content = form.content.data
    username = username
    new_feedback = Feedback(title=title, content=content, username=username)
    db.session.add(new_feedback)
    db.session.commit()
    return new_feedback

def change_feedback(form, feedback):
    feedback.title = form.title.data or feedback.title
    feedback.content = form.content.data or feedback.content
    db.session.commit()

class User(db.Model):

    __tablename__ = 'users'

    username = db.Column(db.String(20), primary_key=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.String(50), unique=True, nullable=False)

    first_name = db.Column(db.String(30), nullable=False)

    last_name = db.Column(db.String(30), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    feedback = db.Relationship('Feedback', backref='user', cascade='all, delete')

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        hashed_pwd = bcrypt.generate_password_hash(pwd)

        decoded_hash = hashed_pwd.decode('utf8')

        return cls(username=username, password=decoded_hash, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

class Feedback(db.Model):

    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(100))

    content = db.Column(db.Text, nullable=False)

    username = db.Column(db.String(20), db.ForeignKey('users.username', ondelete='CASCADE'), nullable=False)

    




