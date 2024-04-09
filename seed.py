from models import db, connect_db, User, Feedback
from app import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

user = User(username='bella', password=bcrypt.generate_password_hash('mylove').decode('utf8'), email='bella.riddell4@gmail.com', first_name='Bella', last_name='Riddell')

db.session.add(user)
db.session.commit()