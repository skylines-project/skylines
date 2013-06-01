def truncate(string, length=50, suffix='...', smart=False):
    if len(string) <= length:
        return string
    elif smart:
        return string[:(length - len(suffix))].rsplit(' ', 1)[0] + suffix
    else:
        return string[:(length - len(suffix))] + suffix
