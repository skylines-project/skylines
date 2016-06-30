import Ember from 'ember';

import { addAltitudeUnit } from '../utils/units';
import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend(Ember.Evented, {
  layoutName: 'components/base-barogram',

  height: 133,

  flot: null,

  active: [],
  passive: [],
  enls: [],

  contests: null,
  elevations: [],

  flotStyle: safeComputed('height', height => Ember.String.htmlSafe(`width: 100%; height: ${height}px;`)),

  draw() {
    this.update();

    let flot = this.get('flot');
    flot.setupGrid();
    flot.draw();
  },

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
  },

  update() {
    let data = [];
    this.addElevations(data);
    this.addActiveTraces(data);
    this.addPassiveTraces(data);
    this.addENLData(data);
    this.addContests(data);

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
});
