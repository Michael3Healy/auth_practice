from flask import Flask, session, redirect, render_template, flash
from models import connect_db, has_admin, no_user_logged_in, change_feedback, create_feedback, db, User, Feedback, create_user, authenticate_user, incorrect_user_logged_in
from forms import RegisterUserForm, LoginUserForm, AddFeedbackForm, UpdateFeedbackForm
from sqlalchemy.exc import IntegrityError
from pdb import set_trace

app = Flask(__name__)

app.config['SQLALCHEMY_ECHO'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_practice'
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.app_context().push()
# connect_db(app)


@app.route('/')
def redirect_to_reg():
    '''Redirect to /register'''
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    '''Shows and handles form that when submitted will register a user'''
    if not no_user_logged_in(session):
        flash('You are already logged in', 'info')
        username = session.get('username')
        return redirect(f'/users/{username}')
    form = RegisterUserForm()
    if form.validate_on_submit():
        try:
            new_user = create_user(form)
        except IntegrityError:
            form.username.errors.append('Username/email taken. Please pick another')
            return render_template('register.html', form=form)

        session['username'] = new_user.username
        flash('Successfully created your account!', 'success')
        return redirect(f'/users/{new_user.username}')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    '''Shows and handles form to login user'''
    if not no_user_logged_in(session):
        flash('You are already logged in', 'info')
        username = session.get('username')
        return redirect(f'/users/{username}')
    form = LoginUserForm()
    if form.validate_on_submit():
        user = authenticate_user(form)
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
    if no_user_logged_in(session):
        flash('Please login first', 'danger')
        return redirect('/login')
    elif incorrect_user_logged_in(session, username):
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
    if no_user_logged_in(session):
        flash('Please login first', 'danger')
        return redirect('/login')
    elif incorrect_user_logged_in(session, username):
        flash('You can only access your own user profile', 'danger')
        return redirect('/')
    db.session.delete(user)
    db.session.commit()
    if has_admin(session):
        logged_in_user = User.query.filter_by(username=session.get('username')).first()
        return redirect(f'/users/{logged_in_user.username}')
    else:
        return redirect('/logout')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    '''Display and handle form for adding feedback'''
    user = User.query.get_or_404(username)
    if no_user_logged_in(session):
        flash('Please login first', 'danger')
        return redirect('/login')
    elif incorrect_user_logged_in(session, username):
        flash('You can only access your own user profile', 'danger')
        return redirect('/')
    form = AddFeedbackForm()
    if form.validate_on_submit():
        new_feedback = create_feedback(form, username)
        flash('Feedback successfully added!', 'success')
        return redirect(f'/users/{username}')
    else:
        return render_template('add_feedback.html', form=form)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    '''Display and handle form for editing feedback'''
    feedback = Feedback.query.get_or_404(feedback_id)
    user = feedback.user
    if no_user_logged_in(session) or incorrect_user_logged_in(session, user.username):
        flash("You can only update your own feedback", 'danger')
        return redirect('/login')
    form = UpdateFeedbackForm()
    if form.validate_on_submit():
        change_feedback(form, feedback)
        return redirect(f'/users/{user.username}')
    else:
        return render_template('update_feedback.html', feedback=feedback, form=form)

@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    '''Delete feedback and redirect to user details page'''
    feedback = Feedback.query.get_or_404(feedback_id)
    user = feedback.user
    if no_user_logged_in(session) or incorrect_user_logged_in(session, user.username):
        flash("You can only update your own feedback", 'danger')
        return redirect('/login')
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{user.username}')