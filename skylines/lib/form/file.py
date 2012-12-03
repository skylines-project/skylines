from tw.forms import FileField


class MultiFileField(FileField):
    """A form field that allows multiple file uploads."""
    attrs = dict(multiple='1')
