from flask import Blueprint, render_template


task_blueprint = Blueprint('task', 'skylines')


@task_blueprint.route('/')
def index():
    return render_template('task/map.jinja')
