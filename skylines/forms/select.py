from wtforms.fields import SelectField as BaseSelectField
from wtforms.validators import ValidationError
from wtforms.widgets import Select as BaseSelectWidget
from wtforms.widgets.core import HTMLString, html_params, escape


__all__ = ('SelectField', 'SelectWidget')


class SelectWidget(BaseSelectWidget):
    """
    Add support of choices with ``optgroup`` to the ``Select`` widget.
    """
    @classmethod
    def render_option(cls, value, label, mixed):
        """
        Render option as HTML tag, but not forget to wrap options into
        ``optgroup`` tag if ``label`` var is ``list`` or ``tuple``.
        """
        if isinstance(label, (list, tuple)):
            children = []

            for item_value, item_label in label:
                item_html = cls.render_option(item_value, item_label, mixed)
                children.append(item_html)

            html = u'<optgroup label="%s">%s</optgroup>'
            data = (escape(unicode(value)), u'\n'.join(children))
        else:
            coerce_func, data = mixed
            selected = coerce_func(value) == data

            options = {'value': value}

            if selected:
                options['selected'] = u'selected'

            html = u'<option %s>%s</option>'
            data = (html_params(**options), escape(unicode(label)))

        return HTMLString(html % data)


class SelectField(BaseSelectField):
    """
    Add support of ``optgorup``'s' to default WTForms' ``SelectField`` class.

    So, next choices would be supported as well::

        (
            ('Fruits', (
                ('apple', 'Apple'),
                ('peach', 'Peach'),
                ('pear', 'Pear')
            )),
            ('Vegetables', (
                ('cucumber', 'Cucumber'),
                ('potato', 'Potato'),
                ('tomato', 'Tomato'),
            ))
        )

    """
    widget = SelectWidget()

    def iter_choices(self):
        """
        We should update how choices are iter to make sure that value from
        internal list or tuple should be selected.
        """
        for value, label in self.choices:
            yield (value, label, (self.coerce, self.data))

    def pre_validate(self, form, choices=None):
        """
        Don't forget to validate also values from embedded lists.
        """
        default_choices = choices is None
        choices = choices or self.choices

        for value, label in choices:
            found = False

            if isinstance(label, (list, tuple)):
                found = self.pre_validate(form, label)

            if found or value == self.data:
                return True

        if not default_choices:
            return False

        raise ValidationError(self.gettext(u'Not a valid choice'))
