from models import db, connect_db, User, Feedback
from app import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

user = User(username='bella', password=bcrypt.generate_password_hash('mylove').decode('utf8'), email='bella.riddell4@gmail.com', first_name='Bella', last_name='Riddell', is_admin=True)
feedback = Feedback(title='Bella Thoughts', content='This is what Bella thinks about')
user.feedback.append(feedback)
db.session.add_all([user, feedback])
db.session.commit()