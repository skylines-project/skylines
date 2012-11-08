from tg import response

def jsonp(func):
    def jsonp_handler(*args, **kw):
        if 'callback' in kw:
            callback = kw.pop('callback')
        else:
            return func(*args, **kw)

        response.content_type = 'application/javascript'
        return '{}({});'.format(callback, func(*args, **kw))
    return jsonp_handler
