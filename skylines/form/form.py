from tw.forms import Form

class BootstrapMixin(object):
    """
    Mix-in class for containers that use a table to render their fields
    """
    params = ["show_labels", "hover_help"]
    show_labels = True
    hover_help = False

class BootstrapForm(Form, BootstrapMixin):
    template = "skylines.templates.form.bootstrap_form"
