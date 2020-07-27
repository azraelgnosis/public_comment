from flask import Blueprint, redirect, render_template, request, url_for
import json

from public_comment.const import *
from public_comment.data import VoxPopuli
from public_comment.db import DataManager
from public_comment.models import Comment

bp = Blueprint('vox', __name__)
vp = VoxPopuli()
dm = DataManager()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/table/', methods=(GET,))
def table():
    table = None        

    return render_template('table.html', table=table)

@bp.route('/load_table', methods=(POST,))
def load_table():
    vp.table = {
        'sheet': request.files['spreadsheet'],
        'header': request.form['header']
    }

    return redirect(url_for('vox.form'))

@bp.route('/form/', methods=[GET])
@bp.route('/form/<string:dir>/<int:track>', methods=[GET])
def form(index:int=None):
    table = vp.table    
    row = vp.get_series(table, index)
    comment = Comment.from_dict(row.to_dict())

    districts = dm.get_districts()  # ['Carla Smith', 'Amir R. Farokhi', 'Antonio Brown', 'Cleta Winslow', 'Natalyn Archibong', 'Jennifer N. Ide', 'Howard Shook', 'J. P. Matzigkeit', 'Dustin Hillis', 'Andrea L. Boone', 'Marci Collier Overstreet', 'Joyce Sheperd']
    # TODO easier way to update keywords
    keywords = ['afford', 'arrest', 'civil', 'community', 'criminal', 'defund', 'dismantle', 'homeless', 'jail', 'officer', 'police', 'policing', 'prison', 'private', 'property', 'public' 'reallocate', 'reform', 'replace', 'school', 'training', 'victim']
    cities = []
    counties = []
    neighborhoods = sorted(dm.get_neighborhoods(), key=lambda neighborhood: neighborhood.name)
    zones = dm.select(ZONES)  # dm.get_zones()
    # npus = dm.get_npus()
    intents = ["For Police (Support Budget)", "Defund Police (Amend Budget)", "Other"] 

    return render_template('form.html', comment=comment, intents=intents, districts=districts, zones=zones, neighborhoods=neighborhoods)

@bp.route('/form/<string:dir>/<int:track>', methods=[POST])
def acknowledge(dir:str, track:int):
    pass