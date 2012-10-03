from __future__ import absolute_import
from markdown import Markdown
from skylines.lib.helpers.urlize import UrlizeExtension

__all__ = ['markdown']

urlize = UrlizeExtension()
markdown = Markdown(extensions=['nl2br', urlize], safe_mode='escape')
