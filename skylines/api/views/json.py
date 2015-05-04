from flask import request, json, current_app


def jsonify(data, status=200, headers=None):
    if not isinstance(data, (dict, list)):
        raise TypeError

    # Determine JSON indentation
    indent = None
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not request.is_xhr:
        indent = 2

    # Determine if this is a JSONP request
    callback = request.args.get('callback', False)
    if callback:
        content = str(callback) + '(' + json.dumps({
            'meta': {
                'status': status,
            },
            'data': data,
        }, indent=indent) + ')'
        mimetype = 'application/javascript'
        status = 200

    else:
        content = json.dumps(data, indent=indent)
        mimetype = 'application/json'

    return current_app.response_class(
        content, mimetype=mimetype, headers=headers), status
