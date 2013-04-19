from webassets.filter.closure import ClosureJS


class SimpleClosureJS(ClosureJS):
    """
    This filter uses the Google Closure Compiler with simple optimizations
    turned on.
    """

    def setup(self):
        super(SimpleClosureJS, self).setup()

        # Configure default closure compiler options
        self.opt = 'SIMPLE_OPTIMIZATIONS'
        self.extra_args = ['--jscomp_off', 'internetExplorerChecks']
