from flask import Blueprint, render_template, request, Response, redirect, url_for
from jinja2.exceptions import TemplateNotFound
import os
import config as config
import shaclform as shacl

routes = Blueprint('controller', __name__)


@routes.route('/')
def form():
    try:
        return render_template('form_contents.html')
    except TemplateNotFound:
        return render_template('generate_form_prompt.html')


@routes.route('/deletefiles')
def deletefiles():
    try:
        os.remove(config.APP_DIR + '/map.ttl')
        os.remove(config.APP_DIR + '/result.ttl')
        # os.remove(config.TEMPLATES_DIR + '/form_contents.html')
        return render_template('generate_form_prompt.html')
    except Exception as e:
        # no file
        return render_template('generate_form_prompt.html')


@routes.route('/generate_form')
def gen_form():
    form_filepath = config.TEMPLATES_DIR + '/form_contents.html'
    map_filepath = 'map.ttl'
    try:
        with open(config.SHAPES_FILE_PATH) as shape:
            shacl.generate_form(shape, form_destination=form_filepath, map_destination=map_filepath)
    except FileNotFoundError:
        return Response('No SHACL shapes file provided at ' + config.SHAPES_FILE_PATH,
                        status=500,
                        mimetype='text/plain')
    return redirect(url_for('controller.form'))


@routes.route('/post', methods=['POST'])
def post():
    try:
        baseuri = 'http://example.org/ex#'
        rdf_result = shacl.Form2RDFController(base_uri=baseuri).convert(request, 'map.ttl')
    except ValueError as e:
        return Response(str(e))
    except FileNotFoundError:
        return Response('Map.ttl is missing!', status=500, mimetype='text/plain')
    rdf_result.serialize(destination='result.ttl', format='turtle')
    return render_template('post.html')

