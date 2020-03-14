# quickanban
## Web Application Assignment - CS162

***

### Table of Contents
1. [Kanban Functionality](#Kanban-Functionality)
2. [Project Structure](#Project-Structure)
3. [Extra Features](#Extra-Features)
4. [Installation Guide](#Installation-Guide)
5. [Unit Testing](#Unit-Testing)

***

### Kanban Functionality

**Headers**
1. To Do
2. Doing
3. Done

**Features**
1. Creating a new task
2. Moving tasks to different states
3. Deleting tasks

***

### Project Structure


***

### Extra Features


***

### Installation Guide

Just type into your command line (while in the project's root directory):

```bash
python3.6 -m venv .venv 
source .venv/bin/activate
pip3 install -r requirements.txt
export FLASK_APP=app.py
flask run
```

***

### Unit Testing

Unit tests can be run using the following command (while in the project’s root directory):

```bash
python3 -m unittest discover test
```

