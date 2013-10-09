from flask_wtf.file import FileField
from wtforms.widgets import FileInput as _FileInput


class FileInput(_FileInput):
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        if self.multiple:
            kwargs['multiple'] = 'multiple'

        return super(FileInput, self).__call__(field, **kwargs)


class MultiFileField(FileField):
    widget = FileInput(multiple=True)
