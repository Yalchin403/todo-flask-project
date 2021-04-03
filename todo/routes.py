import secrets, os
from flask import render_template, url_for, request, redirect, flash
from todo.models import Todo, User
from todo import app, db, bcrypt
from todo.forms import RegistrationForm, LoginForm, UpdateAccountForm,RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
@app.route('/', methods=['GET',])
@login_required
def index():
    user_id = current_user.id
    all_tasks = Todo.query.filter_by(user_id=user_id).order_by(Todo.created_date).all()
    return render_template("index.html", all_tasks=all_tasks)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/create-task', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'GET':
        return render_template("create_task.html")

    task_title = request.form['title']
    task_description = request.form['description']
    user_id = current_user.id
    new_task = Todo(title=task_title, content=task_description, user_id=user_id)
    try:
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    except:
        return "Form you've provided is not valid!"

@app.route('/delete/<int:id>')
@login_required
def delete_task(id):
    target_task = Todo.query.get_or_404(id)
    if target_task.owner.username == current_user.username:
        try:
            db.session.delete(target_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem with deleting the task..."
    
    return "You don't have permission to do that"

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):

    task_to_edit = Todo.query.get_or_404(id)
    if task_to_edit.owner.username == current_user.username:
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
    return "You don't have permission to do that"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template("register.html", title='Register', form=form)
    
    if form.validate_on_submit():
        form = RegistrationForm()
        username = form.username.data
        email = form.email.data
        password = form.password.data
        hashed_pw = bcrypt.generate_password_hash(password). decode('utf-8')
        user = User(username = username, email = email, password = hashed_pw)
        db.session.add(user)
        db.session.commit()
        msg = f'Dear, {username} new account is successfully created for you!'
        form=LoginForm()
        return render_template("login.html", title="Login", form=form, msg=msg)
    
    msg = 'Form is not valid'
    return render_template('register.html', title='Register', form=form, msg = msg)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', title='Login', form=form)


    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('about'))

            msg = "Email or Password incorrect"
            return render_template("login.html", title="Login", form=form, msg=msg)
        
        msg = "User doesn't exists"
        return render_template("login.html", title="Login", form=form, msg=msg)

    msg = "Form is not valid,please check the entries!"
    return render_template("login.html", title="Login", form=form, msg=msg)
    

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

def save_pp_pic(raw_image):
    gen_id = secrets.token_hex(8)
    file_name, file_ext = os.path.splitext(raw_image.filename)
    picture_name = gen_id + file_ext
    absolute_path = os.path.join(app.root_path, 'static/photos', picture_name)
    resize = (125, 125)
    img = Image.open(raw_image)
    img.thumbnail(resize)
    img.save(absolute_path)
    return picture_name


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    user_image = url_for('static', filename = f'photos/{current_user.image_file}')
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        return render_template('account.html', title='Account', user_image=user_image, form=form)
    
    if form.validate_on_submit():
        if form.image.data:
            image = save_pp_pic(form.image.data)
            current_user.image_file = image
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('account'))
    return render_template('account.html', title='Account', user_image=user_image, form=form)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if request.method == 'GET':
        return render_template('reset_request.html', titlle='Resest Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def new_pass(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if request.method == 'GET':
        return render_template('.html', titlle='Resest Password', form=form) # change the name of template