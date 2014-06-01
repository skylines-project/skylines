/*
Flot plugin for selecting times in a flight

The plugin defines the following options:

  selection: {
    mode: null or "x",
    color: color
  }

Selection support is enabled by setting the mode to "x". The user will
only be able to specify the x range. "color" is color of the selection
(if you need to change the color later on, you can get to it with
plot.getOptions().selection.color).

When selection support is enabled, a "plotselected" event will be
emitted on the DOM element you passed into the plot function. The
event handler gets a parameter with the ranges selected on the axes,
like this:

  placeholder.bind("plotselected", function(event, ranges) {
    alert("You selected " + ranges.xaxis.from + " to " + ranges.xaxis.to)
    // with multiple axes, the extra ones are in x2axis, x3axis, ...
  });

The "plotselected" event is only fired when the user has finished
making the selection. A "plotselecting" event is fired during the
process with the same parameters as the "plotselected" event, in case
you want to know what's happening while it's happening,

A "plotunselected" event with no arguments is emitted when the user
clicks the mouse to remove the selection.

The plugin allso adds the following methods to the plot object:

- setSelection(ranges, preventEvent)

  Set the selection range. The passed in ranges is on the same
  form as returned in the "plotselected" event, like this:

    setSelection({ xaxis: { from: 0, to: 10 } });

  setSelection will trigger the "plotselected" event when called. If
  you don't want that to happen, e.g. if you're inside a
  "plotselected" handler, pass true as the second parameter. If you
  are using multiple axes, you can specify the ranges on any of those,
  e.g. as x2axis/x3axis/... instead of xaxis, the plugin picks the
  first one it sees.

- clearSelection(preventEvent)

  Clear the selection rectangle. Pass in true to avoid getting a
  "plotunselected" event.

- getSelection()

  Returns the current selection in the same format as the
  "plotselected" event. If there's currently no selection, the
  function returns null.

*/

(function($) {
  function init(plot) {
    var selection = {
      first: { x: -1}, second: { x: -1},
      show: false,
      active: false
    };

    // FIXME: The drag handling implemented here should be
    // abstracted out, there's some similar code from a library in
    // the navigation plugin, this should be massaged a bit to fit
    // the Flot cases here better and reused. Doing this would
    // make this plugin much slimmer.
    var savedhandlers = {};

    var mouseUpHandler = null;

    function onMouseMove(e) {
      if (selection.active) {
        updateSelection(e);

        plot.getPlaceholder().trigger('plotselecting', [getSelection()]);
      }
    }

    function onMouseDown(e) {
      if (e.which != 1)  // only accept left-click
        return;

      // cancel out any text selections
      document.body.focus();

      // prevent text selection and drag in old-school browsers
      if (document.onselectstart !== undefined && savedhandlers.onselectstart == null) {
        savedhandlers.onselectstart = document.onselectstart;
        document.onselectstart = function() { return false; };
      }
      if (document.ondrag !== undefined && savedhandlers.ondrag == null) {
        savedhandlers.ondrag = document.ondrag;
        document.ondrag = function() { return false; };
      }

      var selected_marker = getMarker(e);

      if (selected_marker == null)
        return;
      else if (selected_marker == 'first')
        setSelectionPos(selection.first, e);
      else
        setSelectionPos(selection.second, e);

      selection.active = selected_marker;

      // this is a bit silly, but we have to use a closure to be
      // able to whack the same handler again
      mouseUpHandler = function(e) { onMouseUp(e); };

      $(document).one('mouseup', mouseUpHandler);
    }

    function onMouseUp(e) {
      mouseUpHandler = null;

      // revert drag stuff for old-school browsers
      if (document.onselectstart !== undefined)
        document.onselectstart = savedhandlers.onselectstart;
      if (document.ondrag !== undefined)
        document.ondrag = savedhandlers.ondrag;

      // no more dragging
      selection.active = null;
      updateSelection(e);

      triggerSelectedEvent();

      return false;
    }

    function getMarker(e) {
      var o = plot.getOptions();
      var offset = plot.getPlaceholder().offset();
      var plotOffset = plot.getPlotOffset();
      var pos = clamp(0, e.pageX - offset.left - plotOffset.left, plot.width());

      var dist_to_first = Math.abs(selection.first.x - pos),
          dist_to_second = Math.abs(selection.second.x - pos);

      if (dist_to_first <= dist_to_second && dist_to_first < 10)
        return 'first';
      else if (dist_to_first > dist_to_second && dist_to_second < 10)
        return 'second';
      else
        return null;
    }

    function getSelection() {
      var r = {}, c1 = selection.first, c2 = selection.second;
      $.each(plot.getAxes(), function(name, axis) {
        if (axis.used) {
          var p1 = axis.c2p(c1[axis.direction]), p2 = axis.c2p(c2[axis.direction]);
          r[name] = { from: Math.min(p1, p2), to: Math.max(p1, p2) };
        }
      });
      return r;
    }

    function triggerSelectedEvent() {
      var r = getSelection();

      plot.getPlaceholder().trigger('plotselected', [r]);

      // backwards-compat stuff, to be removed in future
      if (r.xaxis && r.yaxis)
        plot.getPlaceholder().trigger('selected', [{ x1: r.xaxis.from, x2: r.xaxis.to }]);
    }

    function clamp(min, value, max) {
      return value < min ? min : (value > max ? max : value);
    }

    function setSelectionPos(pos, e) {
      var o = plot.getOptions();
      var offset = plot.getPlaceholder().offset();
      var plotOffset = plot.getPlotOffset();
      pos.x = clamp(0, e.pageX - offset.left - plotOffset.left, plot.width());

    }

    function updateSelection(pos) {
      if (pos.pageX == null)
        return;

      if (selection.active == 'first')
        setSelectionPos(selection.first, pos);
      else if (selection.active == 'second')
        setSelectionPos(selection.second, pos);

      selection.show = true;
      plot.triggerRedrawOverlay();
    }

    function clearSelection(preventEvent) {
      if (selection.show) {
        selection.show = false;
        plot.triggerRedrawOverlay();
        if (!preventEvent)
          plot.getPlaceholder().trigger('plotunselected', []);
      }
    }

    // function taken from markings support in Flot
    function extractRange(ranges, coord) {
      var axis, from, to, key, axes = plot.getAxes();

      for (var k in axes) {
        axis = axes[k];
        if (axis.direction == coord) {
          key = coord + axis.n + 'axis';
          if (!ranges[key] && axis.n == 1)
            key = coord + 'axis'; // support x1axis as xaxis
          if (ranges[key]) {
            from = ranges[key].from;
            to = ranges[key].to;
            break;
          }
        }
      }

      // backwards-compat stuff - to be removed in future
      if (!ranges[key]) {
        axis = coord == 'x' ? plot.getXAxes()[0] : plot.getYAxes()[0];
        from = ranges[coord + '1'];
        to = ranges[coord + '2'];
      }

      // auto-reverse as an added bonus
      if (from != null && to != null && from > to) {
        var tmp = from;
        from = to;
        to = tmp;
      }

      return { from: from, to: to, axis: axis };
    }

    function setSelection(ranges, preventEvent) {
      var axis, range, o = plot.getOptions();

      range = extractRange(ranges, 'x');

      selection.first.x = range.axis.p2c(range.from);
      selection.second.x = range.axis.p2c(range.to);

      selection.show = true;
      plot.triggerRedrawOverlay();
      if (!preventEvent)
        triggerSelectedEvent();
    }

    plot.clearSelection = clearSelection;
    plot.setSelection = setSelection;
    plot.getSelection = getSelection;

    plot.hooks.bindEvents.push(function(plot, eventHolder) {
      var o = plot.getOptions();
      if (o.selection.mode != null) {
        eventHolder.mousemove(onMouseMove);
        eventHolder.mousedown(onMouseDown);
      }
    });


    plot.hooks.drawOverlay.push(function(plot, ctx) {
      // draw selection
      if (selection.show) {
        var plotOffset = plot.getPlotOffset();
        var o = plot.getOptions();

        ctx.save();
        ctx.translate(plotOffset.left, plotOffset.top);

        var c = $.color.parse(o.selection.color);

        ctx.strokeStyle = c.scale('a', 0.8).toString();
        ctx.lineWidth = 1;
        ctx.lineJoin = 'round';
        ctx.fillStyle = c.scale('a', 0.4).toString();

        var y = 0,
            h = plot.height();

        var w_left = Math.min(selection.first.x, selection.second.x);

        ctx.fillRect(0, y, w_left, h);
        ctx.strokeRect(0, y, w_left, h);

        var x_right = Math.max(selection.first.x, selection.second.x);

        ctx.fillRect(x_right, y, plot.width() - x_right, h);
        ctx.strokeRect(x_right, y, plot.width() - x_right, h);

        ctx.restore();
      }
    });

    plot.hooks.shutdown.push(function(plot, eventHolder) {
      eventHolder.unbind('mousemove', onMouseMove);
      eventHolder.unbind('mousedown', onMouseDown);

      if (mouseUpHandler)
        $(document).unbind('mouseup', mouseUpHandler);
    });

  }

  $.plot.plugins.push({
    init: init,
    options: {
      selection: {
        mode: null, // one of null, "x"
        color: '#777777'
      }
    },
    name: 'flight-upload',
    version: '0.9'
  });
})(jQuery);
