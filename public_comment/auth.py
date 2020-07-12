from flask import Blueprint, render_template

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register/')
def register():
    pass

@bp.route('/login/')
def login():
    pass

def logout():
    pass