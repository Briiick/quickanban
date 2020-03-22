# import necessary libraries
from flask import Flask, render_template, request, url_for, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

# start flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'SecretKeyhehehe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 
#/// for relative path
Bootstrap(app)

# configure sql database
db = SQLAlchemy(app) # initialize db
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

'''
TABLES
'''
# create kanban class that is host to 
# column headers of database
class Kanban(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

# user database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

# for individual user logins through id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# login form
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    remember = BooleanField('remember me')

# register form
class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])

'''
KANBAN PAGE
'''
# index (home) page
@app.route('/')
def index():
    return render_template('index.html')

# interacting with kanban task creation
@app.route('/board', methods=['POST', 'GET'])
@login_required
def board():
    # if it's POST, then create new task
    if request.method == 'POST':
        task_content = request.form['content'] # get the content of the input
        new_task = Kanban(content=task_content, status='notstarted') # create new task to be put in db

        # try to commit to database
        try:
            if not task_content:
                return '<h1>Task blank, go back!</h1>'
            else:
                db.session.add(new_task)
                db.session.commit()
                return redirect(url_for('board'))
        except:
            return '<h1>Problem making task!</h1>'
    
    # otherwise (if GET), just query
    else:
        notstarted = Kanban.query.filter_by(status = 'notstarted').order_by(Kanban.last_update).all()
        inprogress = Kanban.query.filter_by(status = 'inprogress').order_by(Kanban.last_update).all()
        completed = Kanban.query.filter_by(status = 'completed').order_by(Kanban.last_update).all()
        return render_template('board.html', notstarted=notstarted, inprogress=inprogress, completed=completed, name=current_user.username)

# delete a task by the id name (primary key)
@app.route('/delete/<int:id>')
def delete(id):
    # get the task by the ID and if it doesn't exist then 404
    task_to_delete = Kanban.query.get_or_404(id)

    # commit to database
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('board'))
    except:
        return '<h1>Problem deleting task!</h1>'

# update task to move it along kanban
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Kanban.query.get_or_404(id)

    if request.method == 'POST':
        task_content = request.form['content']

        try:
            # check task length and make sure not empty
            if not task_content:
                return '<h1>Task blank, go back!</h1>'
            # otherwise commit and return to home page
            task.content = task_content
            task.last_update = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('board'))
        except:
            return '<h1>Issue updating task!</h1>'
    # otherwise, if GET, just query
    else:
        notstarted = Kanban.query.filter_by(status = 'notstarted').order_by(Kanban.last_update).all()
        inprogress = Kanban.query.filter_by(status = 'inprogress').order_by(Kanban.last_update).all()
        completed = Kanban.query.filter_by(status = 'completed').order_by(Kanban.last_update).all()
        return render_template('update.html', task=task, notstarted=notstarted, inprogress=inprogress, completed=completed)

# move task right along board
@app.route('/rightmove/<int:id>/<status>', methods=['GET', 'POST'])
def rightmove(id, status):
    
    task_to_move = Kanban.query.get_or_404(id)

    try:
        # take task and insert into new Column
        # if in not started, put into in Progress
        if status == 'notstarted':
            task_to_move.status = 'inprogress'

        # if in in progress, put into completed
        elif status == 'inprogress':
            task_to_move.status = 'completed'

        task_to_move.last_update = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('board'))
    except:
        return '<h1>Problem moving task!</h1>'
    

# move task left along board
@app.route('/leftmove/<int:id>/<status>', methods=['GET', 'POST'])
def leftmove(id, status):
    
    task_to_move = Kanban.query.get_or_404(id)

    try:
        # take task and insert into new Column
        # if in not started, put into in Progress
        if status == 'inprogress':
            task_to_move.status = 'notstarted'

        # if in in progress, put into completed
        elif status == 'completed':
            task_to_move.status = 'inprogress'

        task_to_move.last_update = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('board'))
    except:
        return '<h1>Problem moving task!</h1>'

'''
IMPLEMENTING USER PROFILES (SIGNUP/LOGIN/LOGOUT)
'''

# register user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    # check if input valid using LoginManager
    if form.validate_on_submit():
        # hash password
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return "<h1>New user has been created. Go to back to login.</a></h1>"

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # take data from login form
    form = LoginForm()

    # check for validation
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # check password
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('board'))

        # if not, output error.
        return '<h1>Invalid username or password. Go back and try again.</h1>'

    return render_template('login.html', form=form)

# implement logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

'''
FAVICON
'''
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')

# run flask app
if __name__ == '__main__':
    app.run(debug=True) # change to false if deploying
