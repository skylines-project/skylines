from __future__ import absolute_import
from markdown import Markdown
from skylines.lib.markdown.urlize import UrlizeExtension

__all__ = ['markdown']

urlize = UrlizeExtension()
markdown = Markdown(extensions=['nl2br', urlize], safe_mode='escape')
