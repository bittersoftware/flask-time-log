from datetime import datetime

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required
from teltech import db
from teltech.models import TimeExpense
from teltech.time_expense.forms import TimeExpenseForm

time_expenses = Blueprint("time_expense", __name__)

MAX_TIME_TO_EDIT_TIME_EXPENSE = 1800    # SECONDS


@time_expenses.route("/time_expense/new", methods=["GET", "POST"])
@login_required
def new_time_expense():
    form = TimeExpenseForm()
    if form.validate_on_submit():
        post = TimeExpense(project=form.project.data, start_date=form.start_date.data, end_date=form.end_date.data, hours_worked=form.hours_worked.data, description=form.description.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your working time has been logged", "success")
        return redirect(url_for("main.home"))
    return render_template("time_expense_form.html", title="New Time Expense", form=form)


def expired_time_to_edit(creation_time):
    current_time = datetime.utcnow()
    creation_time = creation_time
    diff_secs = (current_time - creation_time).total_seconds()
    if diff_secs > MAX_TIME_TO_EDIT_TIME_EXPENSE:
        return True
    else:
        return False


@time_expenses.route("/time_expense/<int:time_expense_id>")
@login_required
def time_expense(time_expense_id):
    time_expense = TimeExpense.query.get_or_404(time_expense_id)
    edit_expired = expired_time_to_edit(time_expense.creation_time)
    if time_expense.user_id == current_user.id:
        return render_template("time_expense.html", time_expense=time_expense, edit_expired=edit_expired)
    else:
        abort(403)


@time_expenses.route("/time_expense/<int:time_expense_id>/update", methods=["GET", "POST"])
@login_required
def time_expense_update(time_expense_id):
    time_expense = TimeExpense.query.get_or_404(time_expense_id)
    if expired_time_to_edit(time_expense.creation_time):
        flash("The period available to edit this data has expired", "danger")
        return redirect(url_for("time_expense.time_expense", time_expense_id=time_expense.id))
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
            return redirect(url_for("time_expense.time_expense", time_expense_id=time_expense.id))
        elif request.method == "GET":
            form.project.data = time_expense.project
            form.start_date.data = time_expense.start_date
            form.end_date.data = time_expense.end_date
            form.hours_worked.data = time_expense.hours_worked
            form.description.data = time_expense.description
        return render_template("time_expense_form.html", legend="Update Time Expense", form=form)
    else:
        abort(403)


@time_expenses.route("/time_expense/<int:time_expense_id>/delete", methods=["POST"])
@login_required
def delete_time_expense(time_expense_id):
    time_expense = TimeExpense.query.get_or_404(time_expense_id)
    if expired_time_to_edit(time_expense.creation_time):
        flash("The period available to delete this data has expired", "danger")
        return redirect(url_for("time_expense.time_expense", time_expense_id=time_expense.id))
    if time_expense.user_id == current_user.id:
        db.session.delete(time_expense)
        db.session.commit()
        flash("Your time expense registration has been removed!", "success")
        return redirect(url_for("main.home"))
    else:
        abort(403)
