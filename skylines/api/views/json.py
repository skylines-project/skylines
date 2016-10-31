from flask import request, json, current_app


def jsonify(data, status=200):
    if not isinstance(data, (dict, list)):
        raise TypeError

    # Determine JSON indentation
    indent = None
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not request.is_xhr:
        indent = 2

    content = json.dumps(data, indent=indent)

    return current_app.response_class(content, mimetype='application/json'), status
