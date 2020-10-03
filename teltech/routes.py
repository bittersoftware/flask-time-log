import os
import secrets
from datetime import datetime

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

from teltech import app, bcrypt, db, mail
from teltech.forms import (LoginForm, RegistrationForm, RequestResetForm,
                           ResetPasswordForm, TimeExpenseForm,
                           UpdateAccountForm)
from teltech.models import TimeExpense, User
from flask_mail import Message

MAX_TIME_TO_EDIT_TIME_EXPENSE = 1800    # SECONDS

@app.route("/")
@app.route("/home")
@login_required
def home():
    page = request.args.get("page", 1, type=int)
    posts = TimeExpense.query.filter_by(user_id=current_user.id).order_by(TimeExpense.creation_time.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)


@app.route("/about")
@login_required
def about():
    return render_template("about.html", title="About")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Ypur account has been created. You are now able to login", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            # TODO delete old image from user
            current_user.image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image = url_for("static",  filename="profile_pics/" + current_user.image)
    return render_template("account.html", title="Account", image=image, form=form)


@app.route("/time_expense/new", methods=["GET", "POST"])
@login_required
def new_time_expense():
    form = TimeExpenseForm()
    if form.validate_on_submit():
        post = TimeExpense(project=form.project.data, start_date=form.start_date.data, end_date=form.end_date.data, hours_worked=form.hours_worked.data, description=form.description.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your working time has been logged", "success")
        return redirect(url_for("home"))
    return render_template("time_expense_form.html", title="New Time Expense", form=form)

def expired_time_to_edit(creation_time):
    current_time = datetime.utcnow()
    creation_time = creation_time
    diff_secs = (current_time - creation_time).total_seconds()
    if diff_secs > MAX_TIME_TO_EDIT_TIME_EXPENSE:
        return True
    else:
        return False

@app.route("/time_expense/<int:time_expense_id>")
@login_required
def time_expense(time_expense_id):
    time_expense = TimeExpense.query.get_or_404(time_expense_id)
    edit_expired = expired_time_to_edit(time_expense.creation_time)
    if time_expense.user_id == current_user.id:
        return render_template("time_expense.html", time_expense=time_expense, edit_expired=edit_expired)
    else:
        abort(403)

@app.route("/time_expense/<int:time_expense_id>/update", methods=["GET", "POST"])
@login_required
def time_expense_update(time_expense_id):
    time_expense = TimeExpense.query.get_or_404(time_expense_id)
    if expired_time_to_edit(time_expense.creation_time):
        flash("The period available to edit this data has expired", "danger")
        return redirect(url_for("time_expense", time_expense_id = time_expense.id))
    if time_expense.user_id == current_user.id:
        form = TimeExpenseForm()
        if form.validate_on_submit():
            time_expense.project = form.project.data 
            time_expense.start_date = form.start_date.data 
            time_expense.end_date = form.end_date.data 
            time_expense.hours_worked = form.hours_worked.data 
            time_expense.description = form.description.data 
            db.session.commit()
            flash("Your hours has been updated", "success")
            return redirect(url_for("time_expense", time_expense_id = time_expense.id))
        elif request.method == "GET":
            form.project.data = time_expense.project
            form.start_date.data = time_expense.start_date
            form.end_date.data = time_expense.end_date
            form.hours_worked.data = time_expense.hours_worked
            form.description.data = time_expense.description
        return render_template("time_expense_form.html", legend="Update Time Expense", form=form)
    else:
        abort(403)
    
@app.route("/time_expense/<int:time_expense_id>/delete", methods=["POST"])
@login_required
def delete_time_expense(time_expense_id):
    time_expense = TimeExpense.query.get_or_404(time_expense_id)
    if expired_time_to_edit(time_expense.creation_time):
        flash("The period available to delete this data has expired", "danger")
        return redirect(url_for("time_expense", time_expense_id = time_expense.id))
    if time_expense.user_id == current_user.id:
        db.session.delete(time_expense)
        db.session.commit()
        flash("Your time expense registration has been removed!", "success")
        return redirect(url_for("home"))
    else:
        abort(403)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", 
                    sender="noreply@demo.com", 
                    recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for("reset_token", token=token,  _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password!", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash(f"Your password has been updated. You are now able to login", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)