


/**
 * An abstraction layer for the barogram view.
 * @param  {DOMElement} placeholder
 * @constructor
 */
function slBarogram(placeholder) {
  /**
   * The flot charts instance.
   * @type {Object}
   * @private
   */
  this.flot_ = null;

  /**
   * The data series that should be drawn as active.
   * @type {Array}
   * @private
   */
  this.active_ = [];

  /**
   * The data series that should be drawn as passive.
   * @type {Array}
   * @private
   */
  this.passive_ = [];

  /**
   * The ENL data series.
   * @type {Array}
   * @private
   */
  this.enls_ = [];

  /**
   * The contest markers.
   * @type {Array}
   * @private
   */
  this.contests_ = [];

  /**
   * The elevation data series.
   * @type {Array}
   * @private
   */
  this.elevations_ = [];

  /**
   * The object describing the highlighted time interval in the barogram.
   * @type {?Object}
   * @private
   */
  this.time_highlight_ = null;

  this.setupFlot_(placeholder);
  this.attachEventHandlers_(placeholder);
}


/**
 * Draws the barogram onto the underlying canvas.
 */
slBarogram.prototype.draw = function() {
  this.update_();
  this.flot_.setupGrid();
  this.flot_.draw();
};


/**
 * Clears the active traces from the barogram.
 */
slBarogram.prototype.clearActiveTraces = function() {
  this.active_ = [];
};


/**
 * Sets the active traces for the barogram.
 * @param {Array} data
 */
slBarogram.prototype.setActiveTraces = function(data) {
  this.active_ = data;
};


/**
 * Clears the passive traces from the barogram.
 */
slBarogram.prototype.clearPassiveTraces = function() {
  this.passive_ = [];
};


/**
 * Sets the passive traces for the barogram.
 * @param {Array} data
 */
slBarogram.prototype.setPassiveTraces = function(data) {
  this.passive_ = data;
};


/**
 * @expose
 * Clears the ENL data.
 */
slBarogram.prototype.clearENLData = function() {
  this.enls_ = [];
};


/**
 * Sets the ENL data.
 * @param {Array} data
 */
slBarogram.prototype.setENLData = function(data) {
  this.enls_ = data;
};


/**
 * Clears the contest markers.
 */
slBarogram.prototype.clearContests = function() {
  this.contests_ = [];
};


/**
 * Sets the contest markers.
 * @param {Array} data
 */
slBarogram.prototype.setContests = function(data) {
  this.contests_ = data;
};


/**
 * Clears the elevation data.
 */
slBarogram.prototype.clearElevations = function() {
  this.elevations_ = [];
};


/**
 * Sets the elevation data.
 * @param {Array} data
 */
slBarogram.prototype.setElevations = function(data) {
  this.elevations_ = data;
};


/**
 * Clears the crosshair from the barogram.
 */
slBarogram.prototype.clearTime = function() {
  this.setTime(null);
};


/**
 * Set the crosshair to the given time.
 *
 * @param {?number} time If null the crosshair is removed,
 *   if -1 the crosshair is moved to the end of the barogram,
 *   else the crosshair is moved to the given time.
 */
slBarogram.prototype.setTime = function(time) {
  if (time === null)
    this.flot_.clearCrosshair();
  else if (time == -1)
    this.flot_.lockCrosshair({x: 999999999});
  else
    this.flot_.lockCrosshair({x: global_time * 1000});
};


/**
 * Clears the time interval limits from the barogram.
 */
slBarogram.prototype.clearTimeInterval = function() {
  var opt = this.flot_.getOptions();
  opt.xaxes[0].min = opt.xaxes[0].max = null;
};


/**
 * Sets the time interval that should be shown on the barogram.
 *
 * @param {number} start The earliest time that should be shown.
 * @param {number} end The latest time that should be shown.
 */
slBarogram.prototype.setTimeInterval = function(start, end) {
  var opt = this.flot_.getOptions();
  opt.xaxes[0].min = start * 1000;
  opt.xaxes[0].max = end * 1000;
};


/**
 * Clears the highlight of a certain time interval from the barogram.
 */
slBarogram.prototype.clearTimeHighlight = function() {
  this.time_highlight_ = null;
};


/**
 * Highlights a certain time interval on the barogram.
 *
 * @param {number} start The earliest time that should be highlighted.
 * @param {number} end The latest time that should be highlighted.
 */
slBarogram.prototype.setTimeHighlight = function(start, end) {
  this.time_highlight_ = {
    start: start,
    end: end
  };
};


/**
 * Sets up the flot charts instance.
 * @param  {DOMElement} placeholder
 * @private
 */
slBarogram.prototype.setupFlot_ = function(placeholder) {
  this.flot_ = $.plot(placeholder, [], {
    grid: {
      borderWidth: 0,
      hoverable: true,
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
};


/**
 * Attaches the external event handlers to the flot charts instance.
 * @param  {DOMElement} placeholder
 * @private
 */
slBarogram.prototype.attachEventHandlers_ = function(placeholder) {
  var that = this;
  placeholder.on('plothover', function(event, pos) {
    $(that).trigger('barohover', [pos.x / 1000.]);
  }).on('mouseout', function(event) {
    $(that).trigger('mouseout');
  });
};


/**
 * Updates the flot charts instance.
 * @private
 */
slBarogram.prototype.update_ = function() {
  var data = [];
  this.addElevations_(data);
  this.addActiveTraces_(data);
  this.addPassiveTraces_(data);
  this.addENLData_(data);
  this.addContests_(data);
  this.updateTimeHighlight_();

  this.flot_.setData(data);
};


/**
 * Adds the active traces to the data series array.
 *
 * @param {Array} data The data array that will be passed to flot.
 * @private
 */
slBarogram.prototype.addActiveTraces_ = function(data) {
  var active_length = this.active_.length;
  for (var i = 0; i < active_length; ++i) {
    var trace = this.active_[i];

    data.push({
      data: trace.data,
      color: trace.color
    });
  }
};


/**
 * Adds the passive traces to the data series array.
 *
 * @param {Array} data The data array that will be passed to flot.
 * @private
 */
slBarogram.prototype.addPassiveTraces_ = function(data) {
  var passive_length = this.passive_.length;
  for (var i = 0; i < passive_length; ++i) {
    var trace = this.passive_[i];

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
};


/**
 * Adds the ENL data to the data series array.
 *
 * @param {Array} data The data array that will be passed to flot.
 * @private
 */
slBarogram.prototype.addENLData_ = function(data) {
  var enls_length = this.enls_.length;
  for (var i = 0; i < enls_length; ++i) {
    var enl = this.enls_[i];

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
};


/**
 * Adds the current contest markers to the data array.
 *
 * @param {Array} data The data array that will be passed to flot.
 * @private
 */
slBarogram.prototype.addContests_ = function(data) {
  // Skip the function if there are no contest markers
  if (this.contests_ === null)
    return;

  // Iterate through the contests
  var contests_length = this.contests_.length;
  for (var i = 0; i < contests_length; ++i) {
    var contest = this.contests_[i];

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
};


/**
 * Adds the elevation data to the data series array.
 *
 * @param {Array} data The data array that will be passed to flot.
 * @private
 */
slBarogram.prototype.addElevations_ = function(data) {
  data.push({
    data: this.elevations_,
    color: 'rgb(235, 155, 98)',
    lines: {
      lineWidth: 0,
      fill: 0.8
    }
  });
};


/**
 * Adds the time highlight area to the flot options if available.
 * @private
 */
slBarogram.prototype.updateTimeHighlight_ = function() {
  // There is no flot.setOptions(), so we modify them in-place.
  var options = this.flot_.getOptions();

  // Clear the markings if there is no time highlight
  if (this.time_highlight_ === null) {
    options.grid.markings = [];
    return;
  }

  // Add time highlight as flot markings
  options.grid.markings = [{
    color: '#fff083',
    xaxis: {
      from: this.time_highlight_.start * 1000,
      to: this.time_highlight_.end * 1000
    }
  }];
};
