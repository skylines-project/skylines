import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { map } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import $ from 'jquery';

export default Component.extend({
  units: service(),

  tagName: '',

  flot: null,

  active: null,
  passive: null,
  enls: null,

  contests: null,
  elevations: null,

  initFlot: action(function (element) {
    this._initFlot(element);
    this.setCrosshair(this.crosshair);
  }),

  _initFlot(element) {
    let units = this.units;

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
          tickFormatter: units.addAltitudeUnit.bind(units),
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

    if (this.uploadMode) {
      opts.selection = {
        mode: 'x',
      };

      opts.crosshair = {
        mode: null,
      };
    }

    let placeholder = $(element);

    this.set('placeholder', placeholder);
    this.set('flot', $.plot(placeholder, [], opts));
  },

  draw: action(function () {
    let flot = this.flot;
    flot.setData(this.data);
    flot.setupGrid();
    flot.draw();
  }),

  data: computed('elevations.[]', 'activeTraces.[]', 'passiveTraces.[]', 'enlData.[]', 'contestData.[]', function () {
    let elevations = {
      data: this.elevations,
      color: 'rgb(235, 155, 98)',
      lines: {
        lineWidth: 0,
        fill: 0.8,
      },
    };

    let data = [elevations];
    data = data.concat(this.activeTraces);
    data = data.concat(this.passiveTraces);
    data = data.concat(this.enlData);
    data = data.concat(this.contestData.filter(Boolean));
    return data;
  }),

  activeTraces: map('active.@each.{data,color}', trace => ({
    data: trace.data,
    color: trace.color,
  })),

  passiveTraces: map('passive.@each.{data,color}', trace => ({
    data: trace.data,
    color: $.color.parse(trace.color).add('a', -0.6).toString(),
    shadowSize: 0,
    lines: {
      lineWidth: 1,
    },
  })),

  enlData: map('enls.@each.{data,color}', enl => ({
    data: enl.data,
    color: enl.color,
    lines: {
      lineWidth: 0,
      fill: 0.2,
    },
    yaxis: 2,
  })),

  contestData: map('contests.@each.{times,color}', contest => {
    let times = contest.times;
    if (times.length < 1) {
      return;
    }

    let color = contest.color;

    // Add the turnpoint markers to the markings array
    let markings = times.map(time => ({
      position: time * 1000,
    }));

    // Add the chart series for this contest to the data array
    return {
      marks: {
        show: true,
        lineWidth: 1,
        toothSize: 6,
        color,
        fillColor: color,
      },
      data: [],
      markdata: markings,
    };
  }),

  setCrosshair: action(function ([crosshair]) {
    if (crosshair) {
      this.flot.lockCrosshair(crosshair);
    } else {
      this.flot.clearCrosshair();
    }
  }),

  setGridMarkings: action(function ([markings]) {
    let options = this.flot.getOptions();
    options.grid.markings = markings;
  }),
});
