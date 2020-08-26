from flask import Blueprint, redirect, render_template, request, url_for
import json

from public_comment.const import *
from public_comment.data import VoxPopuli
from public_comment.db import DataManager
from public_comment.models import Comment, NPU, Zone

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
@bp.route('/form/<string:directory>/<int:track>', methods=[GET])
def form(directory:str=None, track:int=None):
    from flask import current_app
    import os
    sheet = os.path.join(current_app.instance_path, 'Full Council 2020-07-06.xlsx')
    if not vp.table is not None:
        vp.table = {'sheet': sheet, 'header': 2}

    table = vp.table
    row = vp.get_series(table, directory, track)
    comment = Comment.from_dict(row.to_dict())

    districts = dm.get_districts()  # ['Carla Smith', 'Amir R. Farokhi', 'Antonio Brown', 'Cleta Winslow', 'Natalyn Archibong', 'Jennifer N. Ide', 'Howard Shook', 'J. P. Matzigkeit', 'Dustin Hillis', 'Andrea L. Boone', 'Marci Collier Overstreet', 'Joyce Sheperd']
    # TODO easier way to update keywords
    keywords = ['afford', 'arrest', 'city', 'civil', 'community', 'criminal', 'defund', 'dismantle', 'homeless', 'jail', 'npu', 'officer', 'police', 'policing', 'prison', 'private', 'property', 'public' 'reallocate', 'reform', 'replace', 'school', 'training', 'victim', 'zone']
    cities = []
    counties = []
    neighborhoods = sorted(dm.get_neighborhoods(), key=lambda neighborhood: neighborhood.name)
    zones = dm.get_zones()
    npus = dm.get_npus()
    intents = ["For Police (Support Budget)", "Defund Police (Amend Budget)", "Other"] 

    return render_template('form.html', keywords=keywords, comment=comment, intents=intents, districts=districts, zones=zones, neighborhoods=neighborhoods)

@bp.route('/form/<string:directory>/<int:track>', methods=[POST])
def acknowledge(directory:str, track:int):
    acknowledged_comment = Comment.from_dict(request.form)
    vp.update_table(acknowledged_comment)
    
    return redirect(url_for('vox.form', directory=directory, track=track))
