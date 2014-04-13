/**
 * An abstraction layer for the barogram view.
 * @param  {DOMElement} placeholder
 * @constructor
 */
function slBarogram(placeholder) {
  var baro = {};

  // Private attributes

  /**
   * The flot charts instance.
   * @type {Object}
   */
  var flot = null;

  /**
   * The data series that should be drawn as active.
   * @type {Array}
   */
  var active = [];

  /**
   * The data series that should be drawn as passive.
   * @type {Array}
   */
  var passive = [];

  /**
   * The ENL data series.
   * @type {Array}
   */
  var enls = [];

  /**
   * The contest markers.
   * @type {Array}
   */
  var contests = [];

  /**
   * The elevation data series.
   * @type {Array}
   */
  var elevations = [];

  /**
   * The object describing the highlighted time interval in the barogram.
   * @type {?Object}
   */
  var time_highlight = null;

  // Public attributes and methods

  /**
   * Draws the barogram onto the underlying canvas
   */
  baro.draw = function() {
    update();
    flot.setupGrid();
    flot.draw();
  };


  /**
   * Clears the active traces from the barogram
   */
  baro.clearActiveTraces = function() {
    active = [];
  };

  /**
   * Sets the active traces for the barogram
   * @param {Array} data
   */
  baro.setActiveTraces = function(data) {
    active = data;
  };


  /**
   * Clears the passive traces from the barogram
   */
  baro.clearPassiveTraces = function() {
    passive = [];
  };

  /**
   * Sets the passive traces for the barogram
   * @param {Array} data
   */
  baro.setPassiveTraces = function(data) {
    passive = data;
  };


  /**
   * Clears the ENL data
   */
  baro.clearENLData = function() {
    enls = [];
  };

  /**
   * Sets the ENL data
   * @param {Array} data
   */
  baro.setENLData = function(data) {
    enls = data;
  };


  /**
   * Clears the contest markers
   */
  baro.clearContests = function() {
    contests = [];
  };

  /**
   * Sets the contest markers
   * @param {Array} data
   */
  baro.setContests = function(data) {
    contests = data;
  };


  /**
   * Clears the elevation data
   */
  baro.clearElevations = function() {
    elevations = [];
  };

  /**
   * Sets the elevation data
   * @param {Array} data
   */
  baro.setElevations = function(data) {
    elevations = data;
  };


  /**
   * Clears the crosshair from the barogram
   */
  baro.clearTime = function() {
    baro.setTime(null);
  };

  /**
   * Set the crosshair to the given time
   *
   * @param {?number} time If null the crosshair is removed,
   *   if -1 the crosshair is moved to the end of the barogram,
   *   else the crosshair is moved to the given time.
   */
  baro.setTime = function(time) {
    if (time === null)
      flot.clearCrosshair();
    else if (time == -1)
      flot.lockCrosshair({x: 999999999});
    else
      flot.lockCrosshair({x: global_time * 1000});
  };


  /**
   * Clears the time interval limits from the barogram
   */
  baro.clearTimeInterval = function() {
    var opt = flot.getOptions();
    opt.xaxes[0].min = opt.xaxes[0].max = null;
  };

  /**
   * Sets the time interval that should be shown on the barogram
   *
   * @param {number} start The earliest time that should be shown.
   * @param {number} end The latest time that should be shown.
   * @return {Boolean} true if the time interval has changed
   */
  baro.setTimeInterval = function(start, end) {
    var opt = flot.getOptions();
    if (opt.xaxes[0].min != start * 1000 &&
        opt.xaxes[0].max != end * 1000) {
      opt.xaxes[0].min = start * 1000;
      opt.xaxes[0].max = end * 1000;
      return true;
    } else {
      return false;
    }
  };


  /**
   * Clears the highlight of a certain time interval from the barogram
   */
  baro.clearTimeHighlight = function() {
    time_highlight = null;
  };

  /**
   * Highlights a certain time interval on the barogram
   *
   * @param {number} start The earliest time that should be highlighted.
   * @param {number} end The latest time that should be highlighted.
   */
  baro.setTimeHighlight = function(start, end) {
    time_highlight = {
      start: start,
      end: end
    };
  };

  // Initialization

  setupFlot(placeholder);
  attachEventHandlers(placeholder);

  return baro;

  // Private methods

  /**
   * Sets up the flot charts instance.
   * @param  {DOMElement} placeholder
   */
  function setupFlot(placeholder) {
    flot = $.plot(placeholder, [], {
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
    });
  }

  /**
   * Attaches the external event handlers to the flot charts instance.
   * @param  {DOMElement} placeholder
   */
  function attachEventHandlers(placeholder) {
    placeholder.on('plothover', function(event, pos) {
      $(baro).trigger('barohover', [pos.x / 1000.]);
    }).on('plotclick', function(event, pos) {
      $(baro).trigger('baroclick', [pos.x / 1000.]);
    }).on('mouseout', function(event) {
      $(baro).trigger('mouseout');
    });
  }

  /**
   * Updates the flot charts instance
   */
  function update() {
    var data = [];
    addElevations(data);
    addActiveTraces(data);
    addPassiveTraces(data);
    addENLData(data);
    addContests(data);
    updateTimeHighlight();

    flot.setData(data);
  }

  /**
   * Adds the active traces to the data series array
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addActiveTraces(data) {
    var active_length = active.length;
    for (var i = 0; i < active_length; ++i) {
      var trace = active[i];

      data.push({
        data: trace.data,
        color: trace.color
      });
    }
  }

  /**
   * Adds the passive traces to the data series array.
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addPassiveTraces(data) {
    var passive_length = passive.length;
    for (var i = 0; i < passive_length; ++i) {
      var trace = passive[i];

      var color = $.color.parse(trace.color).add('a', -0.6).toString();

      data.push({
        data: trace.data,
        color: color,
        shadowSize: 0,
        lines: {
          lineWidth: 1
        }
      });
    }
  }

  /**
   * Adds the ENL data to the data series array.
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addENLData(data) {
    var enls_length = enls.length;
    for (var i = 0; i < enls_length; ++i) {
      var enl = enls[i];

      data.push({
        data: enl.data,
        color: enl.color,
        lines: {
          lineWidth: 0,
          fill: 0.2
        },
        yaxis: 2
      });
    }
  }

  /**
   * Adds the current contest markers to the data array
   *
   * @param {Array} data The data array that will be passed to flot.
   */
  function addContests(data) {
    // Skip the function if there are no contest markers
    if (contests === null)
      return;

    // Iterate through the contests
    var contests_length = contests.length;
    for (var i = 0; i < contests_length; ++i) {
      var contest = contests[i];

      var times = contest.times;
      var times_length = times.length;
      if (times_length < 1)
        continue;

      var color = contest.color;

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
  function addElevations(data) {
    data.push({
      data: elevations,
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
}
