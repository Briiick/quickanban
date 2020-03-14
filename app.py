# import necessary libraries
from flask import Flask, render_template, request, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# start flask app
app = Flask(__name__)

# configure sql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #/// for relative path
db = SQLAlchemy(app) # initialize db

# create kanban class that is host to 
# column headers of database
class Kanban(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    level = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # return string after creating new element
    def __repr__(self):
        return '<Task %r>' % self.id

# interacting with kanban task creation
@app.route('/', methods=['POST', 'GET'])
def index():
    # if it's POST, then create new task
    if request.method == 'POST':
        task_content = request.form['content'] # get the content of the input
        new_task = Kanban(content=task_content) # create new task to be put in db

        # try to commit to database
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'Problem making task!'
    
    # otherwise (if GET), just query
    else:
        notstarted = Kanban.query.order_by(Kanban.date_created).all()
        return render_template('index.html', notstarted=notstarted)

# delete a task by the id name (primary key)
@app.route('/delete/<int:id>')
def delete(id):
    # get the task by the ID and if it doesn't exist then 404
    task_to_delete = Kanban.query.get_or_404(id)

    # commit to database
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Problem deleting task!'

# update task to move it along kanban
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Kanban.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Issue updating task!'

    else:
        return render_template('update.html', task=task)

if __name__ == '__main__':
    app.run(debug=True)
