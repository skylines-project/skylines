from webassets.filter.closure import ClosureJS


class SimpleClosureJS(ClosureJS):
    """
    This filter uses the Google Closure Compiler with simple optimizations
    turned on.
    """

    def __init__(self, disable_ie_checks=False):
        super(SimpleClosureJS, self).__init__()

        self.disable_ie_checks = disable_ie_checks

    def setup(self):
        super(SimpleClosureJS, self).setup()

        # Configure default closure compiler options
        self.opt = 'SIMPLE_OPTIMIZATIONS'

        if self.disable_ie_checks:
            self.extra_args = ['--jscomp_off', 'internetExplorerChecks']
