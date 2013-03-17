(function() {
  slBarogram = function(placeholder) {
    // Private attributes

    var baro = this;

    var flot = null;

    var active = [];
    var passive = [];
    var enls = [];
    var contests = [];
    var time_highlight = null;

    // Public attributes and functions

    /**
     * @expose
     * Draws the barogram onto the underlying canvas
     */
    baro.draw = function() {
      update();
      flot.setupGrid();
      flot.draw();
    };


    /**
     * @expose
     * Clears the active traces from the barogram
     */
    baro.clearActiveTraces = function() {
      active = [];
    };

    /**
     * @expose
     * Sets the active traces for the barogram
     */
    baro.setActiveTraces = function(data) {
      active = data;
    };


    /**
     * @expose
     * Clears the passive traces from the barogram
     */
    baro.clearPassiveTraces = function() {
      passive = [];
    };

    /**
     * @expose
     * Sets the passive traces for the barogram
     */
    baro.setPassiveTraces = function(data) {
      passive = data;
    };


    /**
     * @expose
     * Clears the ENL data
     */
    baro.clearENLData = function() {
      enls = [];
    };

    /**
     * @expose
     * Sets the ENL data
     */
    baro.setENLData = function(data) {
      enls = data;
    };


    /**
     * @expose
     * Clears the contest markers
     */
    baro.clearContests = function() {
      contests = [];
    };

    /**
     * @expose
     * Sets the contest markers
     */
    baro.setContests = function(data) {
      contests = data;
    };


    /**
     * @expose
     * Clears the crosshair from the barogram
     */
    baro.clearTime = function() {
      baro.setTime(null);
    };

    /**
     * @expose
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
     * @expose
     * Clears the time interval limits from the barogram
     */
    baro.clearTimeInterval = function() {
      var opt = flot.getOptions();
      opt.xaxes[0].min = opt.xaxes[0].max = null;
    };

    /**
     * @expose
     * Sets the time interval that should be shown on the barogram
     *
     * @param {number} start The earliest time that should be shown.
     * @param {number} end The latest time that should be shown.
     */
    baro.setTimeInterval = function(start, end) {
      var opt = flot.getOptions();
      opt.xaxes[0].min = start * 1000;
      opt.xaxes[0].max = end * 1000;
    };


    /**
     * @expose
     * Clears the highlight of a certain time interval from the barogram
     */
    baro.clearTimeHighlight = function() {
      time_highlight = null;
    };

    /**
     * @expose
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

    setupFlot();
    attachEventHandlers();

    function setupFlot() {
      flot = $.plot(placeholder, [], {
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
            tickFormatter: slUnits.add_altitude_unit
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

    function attachEventHandlers() {
      placeholder.on('plothover', function(event, pos) {
        $(baro).trigger('barohover', [pos.x / 1000.]);
      }).on('mouseout', function(event) {
        $(baro).trigger('mouseout');
      });
    }

    function update() {
      var data = [];
      addActiveTraces(data);
      addPassiveTraces(data);
      addENLData(data);
      addContests(data);
      updateTimeHighlight();

      flot.setData(data);
    }

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
  };
})();
