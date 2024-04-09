from unittest import TestCase
from app import app
from models import db, User, Feedback, connect_db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_auth_demo'
app.config['SQLALCHEMY_ECHO'] = False
app.config['WTF_CSRF_ENABLED'] = False
connect_db(app)

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):

    def setUp(self):
        User.query.delete()
        Feedback.query.delete()
        user = User(username='bella', password=bcrypt.generate_password_hash('mylove').decode('utf8'), email='bella.riddell4@gmail.com', first_name='Bella', last_name='Riddell', is_admin=True)
        feedback = Feedback(title='Bella Thoughts', content='This is what Bella thinks about')
        user.feedback.append(feedback)
        db.session.add_all([user, feedback])
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_register_user(self):
        with app.test_client() as client:
            d = {"username": "Stevie", "password": "mickey", "email": "asdf@asdf", "first_name": "Stevie", "last_name": "Chicks"}
            resp = client.post('/register', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Stevie Chicks', html)
            self.assertEqual(User.query.count(), 2)
    
    def test_delete_user(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['username'] = 'bella'
            delete_resp = client.post('/users/bella/delete', follow_redirects=True)
            self.assertEqual(delete_resp.status_code, 200)
            self.assertEqual(User.query.count(), 0)

    