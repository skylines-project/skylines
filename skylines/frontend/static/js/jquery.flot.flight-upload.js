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
      times: { takeoff: -1, landing: -1},
      canvas: { takeoff: -1, landing: -1},
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
      } else {
        var selected_marker = getMarker(e);

        if (selected_marker !== null) {
          plot.getPlaceholder().css('cursor', 'col-resize');
        } else
          plot.getPlaceholder().css('cursor', 'auto');
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
      else if (selected_marker == 'takeoff')
        selection.canvas.takeoff = setSelectionPos(e);
      else
        selection.canvas.landing = setSelectionPos(e);

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

      var dist_to_takeoff = Math.abs(selection.canvas.takeoff - pos),
          dist_to_landing = Math.abs(selection.canvas.landing - pos);

      if (dist_to_takeoff <= dist_to_landing && dist_to_takeoff < 4)
        return 'takeoff';
      else if (dist_to_takeoff > dist_to_landing && dist_to_landing < 4)
        return 'landing';
      else
        return null;
    }

    function getSelection() {
      var r = {}, c1 = selection.canvas.takeoff, c2 = selection.canvas.landing;
      $.each(plot.getAxes(), function(name, axis) {
        if (axis.used) {
          var p1 = axis.c2p(c1[axis.direction]), p2 = axis.c2p(c2[axis.direction]);
          r[name] = { takeoff: Math.min(p1, p2), landing: Math.max(p1, p2) };
        }
      });
      return r;
    }

    function triggerSelectedEvent() {
      var r = getSelection();

      plot.getPlaceholder().trigger('plotselected', [r]);

      // backwards-compat stuff, to be removed in future
      if (r.xaxis && r.yaxis)
        plot.getPlaceholder().trigger('selected', [{ x1: r.xaxis.takeoff, x2: r.xaxis.landing }]);
    }

    function clamp(min, value, max) {
      return value < min ? min : (value > max ? max : value);
    }

    function setSelectionPos(e) {
      var o = plot.getOptions();
      var offset = plot.getPlaceholder().offset();
      var plotOffset = plot.getPlotOffset();
      return clamp(0, e.pageX - offset.left - plotOffset.left, plot.width());

    }

    function updateSelection(pos) {
      if (pos.pageX == null)
        return;

      axis = plot.getXAxes()[0];

      if (selection.active == 'takeoff') {
        selection.times.takeoff = axis.c2p(setSelectionPos(pos));
        selection.times.landing = Math.max(selection.times.takeoff, selection.times.landing);
      } else if (selection.active == 'landing') {
        selection.times.landing = axis.c2p(setSelectionPos(pos));
        selection.times.takeoff = Math.min(selection.times.takeoff, selection.times.landing);
      }

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

    function setSelection(times, preventEvent) {
      var axis, o = plot.getOptions();
      selection.times = times;

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

        axis = plot.getXAxes()[0];
        selection.canvas.takeoff = axis.p2c(selection.times.takeoff);
        selection.canvas.landing = axis.p2c(selection.times.landing);

        ctx.save();
        ctx.translate(plotOffset.left, plotOffset.top);

        var c = $.color.parse(o.selection.color);

        ctx.strokeStyle = c.scale('a', 0.8).toString();
        ctx.lineWidth = 1;
        ctx.lineJoin = 'round';
        ctx.fillStyle = c.scale('a', 0.4).toString();

        var y = 0,
            h = plot.height();

        var w_left = selection.canvas.takeoff;

        ctx.fillRect(0, y, w_left, h);

        var x_right = selection.canvas.landing;

        ctx.fillRect(x_right, y, plot.width() - x_right, h);

        ctx.beginPath();
        ctx.moveTo(w_left, 0);
        ctx.lineTo(w_left, plot.height());
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x_right, 0);
        ctx.lineTo(x_right, plot.height());
        ctx.stroke();

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
