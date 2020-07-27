from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
import functools
from werkzeug.security import check_password_hash, generate_password_hash

from public_comment.const import *
from public_comment.db import DataManager
from public_comment import models

bp = Blueprint(AUTH, __name__, url_prefix='/auth')
dm = DataManager()

@bp.route('/register/', methods=(GET, POST))
def register():
    if request.method == POST:
        new_user_dict = {
            NAME: request.form[NAME].strip(),
            USERNAME: request.form[USERNAME].strip().lower(),
            PASSWORD: generate_password_hash(request.form[PASSWORD].strip())
        }
        new_user = models.User.from_dict(new_user_dict)

        error = None
        if dm.select(USERS, where={USER_VAL: new_user.username}):
            error = "User already exists."

        if not error:
            dm.insert(USERS, values=new_user.to_dict())
            user = dm.select(USERS, where={USER_VAL: new_user.username}, datatype=models.User)[0]
            session.clear()
            session[USER_ID] = user[USER_ID]
            return redirect(url_for('vox.index'))

        flash(error)

    return render_template("auth/register.html")

@bp.route('/login/', methods=(GET, POST))
def login():
    if request.method == POST:
        username = request.form[USERNAME]
        password = request.form[PASSWORD]

        user = dm.select(USERS, where={USER_VAL: username}, datatype=models.User)[0]

        error = None
        if not user:
            error = "User doesn't exist."
        elif not check_password_hash(user.password, password):
            error = "Password is incorrect."

        if not error:
            session.clear()
            session[USER_ID] = user[USER_ID]
            return redirect(url_for('vox.index'))
        
        flash(error)

    return render_template("auth/login.html")

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('vox.index'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get(USER_ID, -1)
    
    try:
        g.user = dm.select('users', where={USER_ID: user_id})[0]
    except IndexError:
        g.user = None
 
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
