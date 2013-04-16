from simplejson import dumps

from tg import response


def jsonp(func):
    def jsonp_handler(*args, **kw):
        if 'callback' in kw:
            response.content_type = 'application/javascript'
            return '{}({});'.format(kw.pop('callback'), dumps(func(*args, **kw)))
        else:
            response.content_type = 'application/json'
            return dumps(func(*args, **kw))

    return jsonp_handler
