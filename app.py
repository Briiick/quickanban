from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/alexanderbricken/Documents/Minerva/CS162/Workspace/kanban_db/kanban.db'

db = SQLAlchemy(app)

class Kanban(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    level = db.Column(db.String)

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    kanban = Kanban(text=request.form['todoitem'], level=0)
    return  redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
