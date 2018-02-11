import { inject as service } from '@ember/service';
import Component from '@ember/component';
import $ from 'jquery';
import { conditional, tag } from 'ember-awesome-macros';
import { htmlSafe } from 'ember-awesome-macros/string';

export default Component.extend({
  units: service(),

  layoutName: 'components/base-barogram',

  height: 133,

  flot: null,

  active: null,
  passive: null,
  enls: null,

  contests: null,
  elevations: null,

  flotStyle: conditional('height', htmlSafe(tag`width: 100%; height: ${'height'}px;`)),

  didInsertElement() {
    this._super(...arguments);
    let units = this.get('units');

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
    this.set('flot', $.plot(placeholder, [], opts));
  },

  draw() {
    this.update();

    let flot = this.get('flot');
    flot.setupGrid();
    flot.draw();
  },

  update() {
    let data = [];
    this.addElevations(data);
    data = data.concat(this.activeTraces());
    data = data.concat(this.passiveTraces());
    data = data.concat(this.enlData());
    this.addContests(data);

    this.get('flot').setData(data);
  },

  activeTraces() {
    return this.get('active').map(trace => ({
      data: trace.data,
      color: trace.color,
    }));
  },

  passiveTraces() {
    return (this.get('passive') || []).map(trace => ({
      data: trace.data,
      color: $.color.parse(trace.color).add('a', -0.6).toString(),
      shadowSize: 0,
      lines: {
        lineWidth: 1,
      },
    }));
  },

  enlData() {
    return this.get('enls').map(enl => ({
      data: enl.data,
      color: enl.color,
      lines: {
        lineWidth: 0,
        fill: 0.2,
      },
      yaxis: 2,
    }));
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
