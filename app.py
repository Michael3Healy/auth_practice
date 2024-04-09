from flask import Flask, session, redirect, render_template, flash
from models import connect_db, db, User, Feedback
from forms import RegisterUserForm, LoginUserForm, AddFeedbackForm, UpdateFeedbackForm
from sqlalchemy.exc import IntegrityError
from pdb import set_trace

app = Flask(__name__)

app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_practice'
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.app_context().push()
connect_db(app)


@app.route('/')
def redirect_to_reg():
    '''Redirect to /register'''
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    '''Shows and handles form that when submitted will register a user'''
    form = RegisterUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username/email taken. Please pick another')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash('Successfully created your account!', 'success')
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    '''Shows and handles form to login user'''
    form = LoginUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back, {user.first_name}', 'info')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user_details(username):
    '''Returns secret text'''
    user = User.query.get_or_404(username)
    if 'username' not in session:
        flash('Please login first', 'danger')
        return redirect('/login')
    elif session['username'] != username:
        flash('You can only access your own user profile', 'danger')
        return redirect('/login')
    else:
        return render_template('user_details.html', user=user)

@app.route('/logout')
def logout_user():
    '''Logout user'''
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    '''Delete user and user's feedback'''
    user = User.query.get_or_404(username)
    if 'username' not in session:
        flash('Please login first', 'danger')
        return redirect('/login')
    elif session['username'] != username:
        flash('You can only access your own user profile', 'danger')
        return redirect('/')
    db.session.delete(user)
    db.session.commit()
    return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    '''Display and handle form for adding feedback'''
    user = User.query.get_or_404(username)
    if 'username' not in session:
        flash('Please login first', 'danger')
        return redirect('/login')
    elif session['username'] != username:
        flash('You can only access your own user profile', 'danger')
        return redirect('/')
    form = AddFeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        username = username
        new_feedback = Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback successfully added!', 'success')
        return redirect(f'/users/{username}')
    else:
        return render_template('add_feedback.html', form=form)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    '''Display and handle form for editing feedback'''
    feedback = Feedback.query.get_or_404(feedback_id)
    user = feedback.user
    form = UpdateFeedbackForm()
    if form.validate_on_submit():
        feedback.title = form.title.data or form.title
        feedback.content = form.content.data or form.content
        db.session.commit()
        return redirect(f'/users/{user.username}')
    else:
        return render_template('update_feedback.html', feedback=feedback, form=form)

@app.route('/feedback/<feedback_id>/delete')
def delete_feedback(feedback_id):
    '''Delete feedback and redirect to user details page'''