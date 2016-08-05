from flask import render_template, request, redirect, url_for, flash
from . import app
from .database import session, Entry, User
from flask_login import login_required, login_user, current_user
from werkzeug.security import check_password_hash

from flask import flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from .database import User

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    
    # Get the limit from the URL and convert it to an integer
    limit = request.args.get('limit', 10)
    
    # Make sure the limit is a positive integer
    try:
        limit = int(limit)
        limit = abs(limit)
    except ValueError:
        limit = 10
    
    # Make sure the limit is greater than zero
    try:
        1/int(limit)
    except ZeroDivisionError:
        limit = 10
    
    if limit > 100:
        limit = 100    
        
    paginate_by = limit    
    
    # Zero-indexed page
    page_index = page - 1
    
    count = session.query(Entry).count()
    
    start = page_index * paginate_by
    end = start + paginate_by
    total_pages = (count - 1) // paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        limit=limit,
        count=count
    )
    
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")
    
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<id>", methods=["GET"])
def view_entry(id):
    entry = session.query(Entry).get(id)
    return render_template("entry.html", id = id, entry = entry)
    
@app.route("/entry/<id>/edit", methods=["GET"])
@login_required
def edit_entry_get(id):
    entry = session.query(Entry).get(id)
    if current_user == entry.author:
        return render_template("edit_entry.html", id = id, entry = entry)
    else:
        return redirect(url_for("entries"))
    
@app.route("/entry/<id>/edit", methods=["POST"])
@login_required
def edit_entry_post(id):
    entry = session.query(Entry).get(id)
    entry.title = request.form["title"]
    entry.content = request.form["content"]
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<id>/delete", methods=["GET"])
@login_required
def delete_entry_get(id):
    entry = session.query(Entry).get(id)
    if current_user == entry.author:
        return render_template("delete_entry.html", id = id, entry = entry)
    else:
        return redirect(url_for("entries"))    

@app.route("/entry/<id>/delete", methods=["POST"])
@login_required
def delete_entry(id):
    entry = session.query(Entry).get(id)
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("entries"))