import Ember from 'ember';

import { addAltitudeUnit } from '../utils/units';

export default Ember.Component.extend(Ember.Evented, {
  layoutName: 'components/base-barogram',

  height: 133,

  flot: null,

  selection: null,

  active: [],
  passive: [],
  enls: [],

  contests: null,
  elevations: [],

  timeHighlight: null,
  hoverMode: false,

  flotStyle: Ember.computed('height', function() {
    return Ember.String.htmlSafe(`width: 100%; height: ${this.get('height')}px;`);
  }),

  draw() {
    this.update();

    let flot = this.get('flot');
    flot.setupGrid();
    flot.draw();
  },

  timeIntervalObserver: Ember.observer('timeInterval', function() {
    this.updateInterval();
  }),

  updateInterval() {
    let { flot, timeInterval: interval } = this.getProperties('flot', 'timeInterval');
    let opt = flot.getOptions();

    if (!interval) {
      opt.xaxes[0].min = opt.xaxes[0].max = null;
    } else {
      let [start, end] = interval;
      opt.xaxes[0].min = start * 1000;
      opt.xaxes[0].max = end * 1000;
    }
  },

  enableFlightSelection() {
    let opt = this.get('flot').getOptions();
    opt.selection.mode = 'x';
  },

  hoverModeObserver: Ember.observer('hoverMode', function() {
    Ember.run.once(this, 'onHoverModeUpdate');
  }),

  didInsertElement() {
    let opts = {
      grid: {
        borderWidth: 0,
        hoverable: true,
        clickable: true,
        autoHighlight: false,
        margin: 5,
      },
      xaxis: {
        mode: 'time',
        timeformat: '%H:%M',
      },
      yaxes: [
        {
          min: 0,
          tickFormatter: addAltitudeUnit,
        },
        {
          show: false,
          min: 0,
          max: 1000,
        },
      ],
      crosshair: {
        mode: 'x',
      },
    };

    if (this.get('uploadMode')) {
      opts.selection = {
        mode: 'x',
      };

      opts.crosshair = {
        mode: null,
      };
    }

    let placeholder = this.$('div');

    this.set('placeholder', placeholder);
    this.set('flot', Ember.$.plot(placeholder, [], opts));

    placeholder.on('plotclick', (event, pos) => {
      this.trigger('baroclick', pos.x / 1000);
    });

    placeholder.on('plotselecting', (event, range, marker) => {
      this.trigger('baroselecting', range, marker);
    });

    this.onHoverModeUpdate();
  },

  onHoverModeUpdate() {
    let placeholder = this.get('placeholder');

    if (this.get('hoverMode')) {
      placeholder.on('plothover', (event, pos) => {
        this.trigger('barohover', pos.x / 1000);
      });

      placeholder.on('mouseout', () => {
        this.trigger('mouseout');
      });
    } else {
      placeholder.off('plothover');
      placeholder.off('mouseout');
    }
  },

  update() {
    let data = [];
    this.addElevations(data);
    this.addActiveTraces(data);
    this.addPassiveTraces(data);
    this.addENLData(data);
    this.addContests(data);
    this.updateTimeHighlight();

    this.get('flot').setData(data);
  },

  addActiveTraces(data) {
    this.get('active').forEach(trace => {
      data.push({
        data: trace.data,
        color: trace.color,
      });
    });
  },

  addPassiveTraces(data) {
    this.get('passive').forEach(trace => {
      let color = Ember.$.color.parse(trace.color).add('a', -0.6).toString();

      data.push({
        data: trace.data,
        color,
        shadowSize: 0,
        lines: {
          lineWidth: 1,
        },
      });
    });
  },

  addENLData(data) {
    this.get('enls').forEach(enl => {
      data.push({
        data: enl.data,
        color: enl.color,
        lines: {
          lineWidth: 0,
          fill: 0.2,
        },
        yaxis: 2,
      });
    });
  },

  addContests(data) {
    // Skip the function if there are no contest markers
    let contests = this.get('contests');
    if (!contests) {
      return;
    }

    // Iterate through the contests
    contests.forEach(contest => {
      let times = contest.get('times');
      if (times.length < 1) {
        return;
      }

      let color = contest.get('color');

      // Add the turnpoint markers to the markings array
      let markings = times.map(time => ({
        position: time * 1000,
      }));

      // Add the chart series for this contest to the data array
      data.push({
        marks: {
          show: true,
          lineWidth: 1,
          toothSize: 6,
          color,
          fillColor: color,
        },
        data: [],
        markdata: markings,
      });
    });
  },

  addElevations(data) {
    data.push({
      data: this.get('elevations'),
      color: 'rgb(235, 155, 98)',
      lines: {
        lineWidth: 0,
        fill: 0.8,
      },
    });
  },

  updateTimeHighlight() {
    // There is no flot.setOptions(), so we modify them in-place.
    let options = this.get('flot').getOptions();

    // Clear the markings if there is no time highlight
    let time_highlight = this.get('timeHighlight');
    if (!time_highlight) {
      options.grid.markings = [];
      return;
    }

    // Add time highlight as flot markings
    options.grid.markings = [{
      color: '#fff083',
      xaxis: {
        from: time_highlight.start * 1000,
        to: time_highlight.end * 1000,
      },
    }];
  },

  timeHighlightObserver: Ember.observer('timeHighlight', function() {
    Ember.run.once(this, 'draw');
  }),
});
