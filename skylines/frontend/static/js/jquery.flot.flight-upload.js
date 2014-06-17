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
      times: { takeoff: -1, scoring_start: -1, scoring_end: -1, landing: -1},
      canvas: { takeoff: -1, scoring_start: -1, scorint_end: -1, landing: -1},
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
      if (selection.active && e.pageX != null) {
        var axis = plot.getXAxes()[0];
        value = axis.c2p(setSelectionPos(e));
        updateSelection(value, selection.active);

        plot.getPlaceholder()
            .trigger('plotselecting', [getSelection(), selection.active]);
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
      if (document.onselectstart !== undefined &&
          savedhandlers.onselectstart == null) {
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
      else if (selected_marker == 'scoring_start')
        selection.canvas.scoring_start = setSelectionPos(e);
      else if (selected_marker == 'scoring_end')
        selection.canvas.scoring_end = setSelectionPos(e);
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
      updateSelection();

      triggerSelectedEvent();

      return false;
    }

    function getMarker(e) {
      var o = plot.getOptions();
      var offset = plot.getPlaceholder().offset();
      var plotOffset = plot.getPlotOffset();
      var pos = clamp(0, e.pageX - offset.left - plotOffset.left, plot.width());

      var min = 4;
      var selected = null;

      for (var index in selection.canvas) {
        var dist = Math.abs(selection.canvas[index] - pos);
        if (dist <= min) {
          selected = index;
          min = dist;
        }
      }

      return selected;
    }

    function getSelection() {
      return {
        takeoff: selection.times.takeoff,
        scoring_start: selection.times.scoring_start,
        scoring_end: selection.times.scoring_end,
        landing: selection.times.landing
      };
    }

    function triggerSelectedEvent() {
      var r = getSelection();

      plot.getPlaceholder().trigger('plotselected', [r, selection.active]);
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

    function updateSelection(value, active) {
      var times = selection.times;

      if (active == 'takeoff') {
        times.takeoff = value;

        times.scoring_start = Math.max(times.takeoff, times.scoring_start);
        times.scoring_end = Math.max(times.takeoff, times.scoring_end);
        times.landing = Math.max(times.takeoff, times.landing);

      } else if (active == 'scoring_start') {
        times.scoring_start = value;

        times.takeoff = Math.min(times.scoring_start, times.takeoff);
        times.scoring_end = Math.max(times.scoring_start, times.scoring_end);
        times.landing = Math.max(times.scoring_start, times.landing);

      } else if (active == 'scoring_end') {
        times.scoring_end = value;

        times.takeoff = Math.min(times.scoring_end, times.takeoff);
        times.scoring_start = Math.min(times.scoring_end, times.scoring_start);
        times.landing = Math.max(times.scoring_end, times.landing);

      } else if (active == 'landing') {
        times.landing = value;

        times.takeoff = Math.min(times.landing, times.takeoff);
        times.scoring_start = Math.min(times.landing, times.scoring_start);
        times.scoring_end = Math.min(times.landing, times.scoring_end);
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
    plot.updateSelection = updateSelection;

    plot.hooks.bindEvents.push(function(plot, eventHolder) {
      var o = plot.getOptions();
      if (o.selection.mode != null) {
        eventHolder.on('mousemove', onMouseMove);
        eventHolder.on('mousedown', onMouseDown);
      }
    });


    plot.hooks.drawOverlay.push(function(plot, ctx) {
      // draw selection
      if (selection.show) {
        var plotOffset = plot.getPlotOffset();
        var o = plot.getOptions();

        axis = plot.getXAxes()[0];
        selection.canvas.takeoff = axis.p2c(selection.times.takeoff);
        selection.canvas.scoring_start =
            axis.p2c(selection.times.scoring_start);
        selection.canvas.scoring_end = axis.p2c(selection.times.scoring_end);
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


        var c_start = $.color.parse(o.selection.scoring_start_color);
        ctx.strokeStyle = c_start.scale('a', 0.8).toString();

        ctx.beginPath();
        ctx.moveTo(selection.canvas.scoring_start, 0);
        ctx.lineTo(selection.canvas.scoring_start, plot.height());
        ctx.stroke();

        var c_end = $.color.parse(o.selection.scoring_end_color);
        ctx.strokeStyle = c_end.scale('a', 0.8).toString();

        ctx.beginPath();
        ctx.moveTo(selection.canvas.scoring_end, 0);
        ctx.lineTo(selection.canvas.scoring_end, plot.height());
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
        color: '#777777',
        scoring_start_color: '#008800',
        scoring_end_color: '#880000'
      }
    },
    name: 'flight-upload',
    version: '0.9'
  });
})(jQuery);
