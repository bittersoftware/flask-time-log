from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from teltech.models import TimeExpense

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
@login_required
def home():
    page = request.args.get("page", 1, type=int)
    posts = TimeExpense.query.filter_by(user_id=current_user.id).order_by(TimeExpense.creation_time.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)


@main.route("/about")
@login_required
def about():
    return render_template("about.html", title="About")
