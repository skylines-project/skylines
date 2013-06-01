from markdown import Markdown

from .urlize import UrlizeExtension

__all__ = ['markdown']

urlize = UrlizeExtension()
markdown = Markdown(extensions=['nl2br', urlize], safe_mode='escape')
