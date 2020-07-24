from flask import Blueprint, redirect, render_template, request, url_for
import json

from public_comment.const import *
from public_comment.data import VoxPopuli

bp = Blueprint('vox', __name__)
vp = VoxPopuli()

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

@bp.route('/form/', methods=(GET, POST))
@bp.route('/form/<int:index>', methods=(GET, POST))
def form(index:int=None):
    row = None
    table = vp.table
    if request.method == POST:
        if spreadsheet := request.files['spreadsheet']:
            header = request.form['header']
            table = vp.set_table(spreadsheet, header)
            
    row = vp.get_row(table, index)
    council_districts = ['Carla Smith', 'Amir R. Farokhi', 'Antonio Brown', 'Cleta Winslow', 'Natalyn Archibong', 'Jennifer N. Ide', 'Howard Shook', 'J. P. Matzigkeit', 'Dustin Hillis', 'Andrea L. Boone', 'Marci Collier Overstreet', 'Joyce Sheperd', 'Michael Julian Bond', 'Matt Westmoreland', 'Andre Dickens']
    # TODO easier to way update keywords
    keywords = ['afford', 'arrest', 'civil', 'community', 'criminal', 'defund', 'dismantle', 'homeless', 'jail', 'officer', 'police', 'policing', 'prison', 'private', 'property', 'public' 'reallocate', 'reform', 'replace', 'school', 'training', 'victim']
    cities = []
    counties = []
    neighborhoods = []
    intents = ["For Police (Support Budget)", "Defund Police (Amend Budget)", "Other"] 

    return render_template('form.html', row=row, intents=intents)
