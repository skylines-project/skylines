from __future__ import absolute_import

import math

from voluptuous.validators import Range


class Approx(Range):
    """
    Similar to the ``approx()`` implementation in pytest
    """

    DEFAULT_ABSOLUTE_TOLERANCE = 1e-12
    DEFAULT_RELATIVE_TOLERANCE = 1e-6

    def __init__(self, expected, abs=None, rel=None, msg=None):
        tolerance = Approx.calculate_tolerance(expected, abs, rel)
        min = expected - tolerance
        max = expected + tolerance

        Range.__init__(self, min=min, max=max, msg=msg)

    @classmethod
    def calculate_tolerance(cls, expected, _abs, _rel):
        """
        Return the tolerance for the comparison.  This could be either an
        absolute tolerance or a relative tolerance, depending on what the user
        specified or which would be larger.
        """

        def set_default(x, default):
            return x if x is not None else default

        # Figure out what the absolute tolerance should be.  ``self.abs`` is
        # either None or a value specified by the user.
        absolute_tolerance = set_default(_abs, cls.DEFAULT_ABSOLUTE_TOLERANCE)

        if absolute_tolerance < 0:
            raise ValueError(
                "absolute tolerance can't be negative: {}".format(absolute_tolerance)
            )
        if math.isnan(absolute_tolerance):
            raise ValueError("absolute tolerance can't be NaN.")

        # If the user specified an absolute tolerance but not a relative one,
        # just return the absolute tolerance.
        if _rel is None:
            if _abs is not None:
                return absolute_tolerance

        # Figure out what the relative tolerance should be.  ``rel`` is
        # either None or a value specified by the user.  This is done after
        # we've made sure the user didn't ask for an absolute tolerance only,
        # because we don't want to raise errors about the relative tolerance if
        # we aren't even going to use it.
        relative_tolerance = set_default(_rel, cls.DEFAULT_RELATIVE_TOLERANCE) * abs(
            expected
        )

        if relative_tolerance < 0:
            raise ValueError(
                "relative tolerance can't be negative: {}".format(absolute_tolerance)
            )
        if math.isnan(relative_tolerance):
            raise ValueError("relative tolerance can't be NaN.")

        # Return the larger of the relative and absolute tolerances.
        return max(relative_tolerance, absolute_tolerance)
