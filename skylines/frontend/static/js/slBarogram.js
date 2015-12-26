/**
 * An abstraction layer for the barogram view.
 * @param  {DOMElement} placeholder
 * @param  {Object=} opt_options Optional options.
 * @constructor
 */
var slBarogramView = Backbone.View.extend((function() {
  // Private attributes

  /**
   * The flot charts instance.
   * @type {Object}
   */
  var flot = null;

  /**
   * The object describing the highlighted time interval in the barogram.
   * @type {?Object}
   */
  var time_highlight = null;

  /**
   * Flag whether the baro will emit a plothover event.
   * @type {Bool}
   */
  var plot_hover = false;

  /**
   * Sets up the flot charts instance.
   * @param  {DOMElement} placeholder
   * @param  {Object} options Additional options.
   */
  function setupFlot(placeholder, options) {
    var opts = {
      grid: {
        borderWidth: 0,
        hoverable: true,
        clickable: true,
        autoHighlight: false,
        margin: 5
      },
      xaxis: {
        mode: 'time',
        timeformat: '%H:%M'
      },
      yaxes: [
        {
          min: 0,
          tickFormatter: slUnits.addAltitudeUnit
        },
        {
          show: false,
          min: 0,
          max: 1000
        }
      ],
      crosshair: {
        mode: 'x'
      }
    };

    $.extend(opts, options);

    flot = $.plot(placeholder, [], opts);
  }

  /**
   * Updates the flot charts instance
   */
  function update(collection) {
    var data = [];

    collection.each(function(flight) {
      if (flight.getSelection() || collection.length == 1) {
        addActiveTraces(data, flight);
        addENLData(data, flight);
      } else {
        addPassiveTraces(data, flight);
      }

      // Save contests of highlighted flight for later
      if (flight.getSelection() || collection.length == 1) {
        addContests(data, flight);
        addElevations(data, flight);
      }
    }.bind(this));

    updateTimeHighlight();

    flot.setData(data);
  }

  /**
   * Adds the active traces to the data series array
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addActiveTraces(data, flight) {
    data.push({
      data: flight.getFlotHeight(),
      color: flight.getColor()
    });
  }

  /**
   * Adds the passive traces to the data series array.
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addPassiveTraces(data, flight) {
    var color = $.color.parse(flight.getColor()).add('a', -0.6).toString();

    data.push({
      data: flight.getFlotHeight(),
      color: color,
      shadowSize: 0,
      lines: {
        lineWidth: 1
      }
    });
  }

  /**
   * Adds the ENL data to the data series array.
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addENLData(data, flight) {
    data.push({
      data: flight.getFlotENL(),
      color: flight.getColor(),
      lines: {
        lineWidth: 0,
        fill: 0.2
      },
      yaxis: 2
    });
  }

  /**
   * Adds the current contest markers to the data array
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addContests(data, flight) {
    contests = flight.getContests();

    // Skip the function if there are no contest markers
    if (contests === null)
      return;

    // Iterate through the contests
    var contests_length = contests.length;
    for (var i = 0; i < contests_length; ++i) {
      var contest = contests[i];

      var times = contest.getTimes();
      var times_length = times.length;
      if (times_length < 1)
        continue;

      var color = contest.getColor();

      // Add the turnpoint markers to the markings array
      var markings = [];
      for (var j = 0; j < times_length; ++j) {
        var time = times[j] * 1000;

        markings.push({
          position: time
        });
      }

      // Add the chart series for this contest to the data array
      data.push({
        marks: {
          show: true,
          lineWidth: 1,
          toothSize: 6,
          color: color,
          fillColor: color
        },
        data: [],
        markdata: markings
      });
    }
  }

  /**
   * Adds the elevation data to the data series array
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addElevations(data, flight) {
    data.push({
      data: flight.getFlotElev(),
      color: 'rgb(235, 155, 98)',
      lines: {
        lineWidth: 0,
        fill: 0.8
      }
    });
  }

  /**
   * Adds the time highlight area to the flot options if available
   */
  function updateTimeHighlight() {
    // There is no flot.setOptions(), so we modify them in-place.
    var options = flot.getOptions();

    // Clear the markings if there is no time highlight
    if (time_highlight === null) {
      options.grid.markings = [];
      return;
    }

    // Add time highlight as flot markings
    options.grid.markings = [{
      color: '#fff083',
      xaxis: {
        from: time_highlight.start * 1000,
        to: time_highlight.end * 1000
      }
    }];
  }

  // Public attributes
  return {
    initialize: function() {
      setupFlot(this.el, this.attributes);
      this.render();

      // Attaches the external event handlers to the flot charts instance.
      this.$el.on('plotclick', function(event, pos) {
        this.trigger('baroclick', [pos.x / 1000.]);
      }.bind(this));

      // Listen to updates of the flight collection
      this.listenTo(this.collection, 'change:selection', function() {
        this.render();
      }.bind(this));
    },

    /**
     * Draws the barogram onto the underlying canvas
     */
    render: function() {
      update(this.collection);
      flot.setupGrid();
      flot.draw();
    },

    /**
     * Clears the crosshair from the barogram
     */
    clearTime: function() {
      this.setTime(null);
    },

    /**
     * Set the crosshair to the given time
     *
     * @param {?number} time If null the crosshair is removed,
     *   if -1 the crosshair is moved to the end of the barogram,
     *   else the crosshair is moved to the given time.
     */
    setTime: function(time) {
      if (time === null)
        flot.clearCrosshair();
      else if (time == -1)
        flot.lockCrosshair({x: 999999999});
      else
        flot.lockCrosshair({x: time * 1000});
    },

    /**
     * Clears the time interval limits from the barogram
     */
    clearTimeInterval: function() {
      var opt = flot.getOptions();
      opt.xaxes[0].min = opt.xaxes[0].max = null;
    },

    /**
     * Sets the time interval that should be shown on the barogram
     *
     * @param {number} start The earliest time that should be shown.
     * @param {number} end The latest time that should be shown.
     * @return {Boolean} true if the time interval has changed
     */
    setTimeInterval: function(start, end) {
      var opt = flot.getOptions();
      if (opt.xaxes[0].min != start * 1000 ||
          opt.xaxes[0].max != end * 1000) {
        opt.xaxes[0].min = start * 1000;
        opt.xaxes[0].max = end * 1000;
        return true;
      } else {
        return false;
      }
    },

    /**
     * Enable flight selection for upload page
     */
    enableFlightSelection: function() {
      var opt = flot.getOptions();

      opt.selection.mode = 'x';
    },

    /**
     * Clears the highlight of a certain time interval from the barogram
     */
    clearTimeHighlight: function() {
      time_highlight = null;
    },

    /**
     * Highlights a certain time interval on the barogram
     *
     * @param {number} start The earliest time that should be highlighted.
     * @param {number} end The latest time that should be highlighted.
     */
    setTimeHighlight: function(start, end) {
      time_highlight = {
        start: start,
        end: end
      };
    },

    /**
     * Highlights the selected flight with takeoff, release and landing
     *
     * @param {number} takeoff The takeoff time.
     * @param {number} scoring_start The scoring window start time.
     * @param {number} scoring_end The scoring window end time.
     * @param {number} landing The landing time.
     */
    setFlightTimes: function(takeoff, scoring_start, scoring_end, landing) {
      flot.setSelection({
        takeoff: takeoff * 1000,
        scoring_start: scoring_start * 1000,
        scoring_end: scoring_end * 1000,
        landing: landing * 1000
      });
    },

    /**
     * Update the highlights the selected flight with takeoff,
     * release and landing
     *
     * @param {number} time The time to set to.
     * @param {string} field The field name to set.
     */
    updateFlightTime: function(time, field) {
      flot.updateSelection(time * 1000, field);
    },

    /**
     * Get the current marker positions
     * @return {Boolean} current selection.
     */
    getFlightTime: function() {
      return flot.getSelection();
    },

    setHoverMode: function(_hover_mode) {
      if (_hover_mode) {
        this.$el.on('plothover', function(event, pos) {
          this.trigger('barohover', pos.x / 1000.);
        }.bind(this));

        this.$el.on('mouseout', function(event) {
          this.trigger('mouseout');
        }.bind(this));
      } else {
        this.$el.off('plothover');
        this.$el.off('mouseout');
      }

      plot_hover = _hover_mode;
    }
  };
})());
