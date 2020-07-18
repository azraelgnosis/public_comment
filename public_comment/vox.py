from flask import Blueprint, render_template, request
import json

from public_comment.const import *
from public_comment.data import VoxPopuli

bp = Blueprint('vox', __name__)
vp = VoxPopuli()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/table/', methods=(GET, POST))
def table():
    table = None
    if request.method == POST:
        table = vp.read_xlsx(
            request.files['spreadsheet'],
            header=request.form['header']
            ).to_html()

    return render_template('table.html', table=table)

@bp.route('/form/', methods=(GET, POST))
@bp.route('/form/<int:index>', methods=(GET, POST))
def form(index:int=None):
    row = table = None
    if request.method == POST:
        if spreadsheet := request.files['spreadsheet']:
            header = request.form['header']
            table = vp.set_table(spreadsheet, header)
            
    row = vp.get_row(table, index)
    council_districts = ['Carla Smith', 'Amir R. Farokhi', 'Antonio Brown', 'Cleta Winslow']
    keywords = ['defund', 'reform', 'reallocate', 'training', 'dismantle', 'replace', 'jail', 'prison', 'community']

    return render_template('form.html', row=row)