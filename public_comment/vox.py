from flask import Blueprint, render_template
import json

bp = Blueprint('vox', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/vox/')
def vox():
    SENTIMENTS = {
        'police': ['defund', 'reform', 'abolish', 'support'],
        'corrections/jail': ['defund'],
        'invest in': ['communities', 'education', 'healthcare', 'other']
    }

    council_districts = ['Carla Smith', 'Amir R. Farokhi', 'Antonio Brown', 'Cleta Winslow']

    keywords = ['defund', 'reform', 'reallocate', 'training', 'dismantle', 'replace', 'jail', 'prison', 'community']
    return render_template('vox.html', sentiments_dict=SENTIMENTS, council_districts=council_districts, keywords=json.dumps(keywords))