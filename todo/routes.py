from flask import render_template, url_for, request, redirect
from todo.models import Todo
from todo import app, db

@app.route('/', methods=['GET',])
def index():
    all_tasks = Todo.query.order_by(Todo.created_date).all()
    return render_template("index.html", all_tasks=all_tasks)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/create-task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'GET':
        return render_template("create_task.html")

    task_title = request.form['title']
    task_description = request.form['description']
    new_task = Todo(title=task_title, content=task_description)
    try:
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    except:
        return "Form you've provided is not valid!"

@app.route('/delete/<int:id>')
def delete_task(id):
    target_task = Todo.query.get_or_404(id)
    try:
        db.session.delete(target_task)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem with deleting the task..."

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):

    task_to_edit = Todo.query.get_or_404(id)
    if request.method == 'GET':
        return render_template("edit.html", task_to_edit=task_to_edit)
    
    task_title = request.form['title']
    task_description = request.form['description']

    try:
        task_to_edit.title = task_title
        task_to_edit.content = task_description
        db.session.commit()
        return redirect('/')
    except:
        return "There was an error while updating the task..."