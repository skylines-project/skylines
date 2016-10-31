from flask import request, json, current_app


def jsonify(_data=None, **kwargs):
    if _data is None:
        _data = kwargs

    if not isinstance(_data, (dict, list)):
        raise TypeError

    # Determine JSON indentation
    indent = None
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not request.is_xhr:
        indent = 2

    content = json.dumps(_data, indent=indent)

    return current_app.response_class(content, mimetype='application/json')
