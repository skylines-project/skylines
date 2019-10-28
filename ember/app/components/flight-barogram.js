import { action, observer, computed } from '@ember/object';

import safeComputed from '../computed/safe-computed';
import BarogramComponent from './base-barogram';

export default BarogramComponent.extend({
  flights: null,
  time: null,
  defaultTime: null,

  flightsObserver: observer('flights.[]', function() {
    this.draw();
  }),

  selection: null,

  activeFlights: computed('flights.[]', 'selection', function() {
    let { flights, selection } = this;
    return flights.filter(flight => !selection || flight.get('id') === selection);
  }),

  passiveFlights: computed('flights.[]', 'selection', function() {
    let { flights, selection } = this;
    return flights.filter(flight => selection && flight.get('id') !== selection);
  }),

  active: computed('activeFlights.@each.{flot_h,color}', function() {
    return this.activeFlights.map(flight => ({
      data: flight.get('flot_h'),
      color: flight.get('color'),
    }));
  }),

  passive: computed('passiveFlights.@each.{flot_h,color}', function() {
    return this.passiveFlights.map(flight => ({
      data: flight.get('flot_h'),
      color: flight.get('color'),
    }));
  }),

  enls: computed('activeFlights.@each.{flot_enl,color}', function() {
    return this.activeFlights.map(flight => ({
      data: flight.get('flot_enl'),
      color: flight.get('color'),
    }));
  }),

  selectedFlight: computed('flights.@each.id', 'selection', function() {
    if (this.flights.length === 1) {
      return this.flights[0];
    }

    if (this.selection) {
      return this.flights.findBy('id', this.selection);
    }
  }),

  contests: safeComputed('selectedFlight', flight => flight.get('contests')),
  elevations: safeComputed('selectedFlight', flight => flight.get('flot_elev')),

  timeInterval: null,

  initFlot: action(function(element) {
    this._initFlot(element);

    this.onHoverModeUpdate();

    this.placeholder.on('plotclick', (event, pos) => {
      this.set('time', pos.x / 1000);
    });
  }),

  didUpdateAttrs() {
    this._super(...arguments);
    let selection = this.selection;
    let timeInterval = this.timeInterval;
    let timeHighlight = this.timeHighlight;
    let hoverMode = this.hoverMode;

    if (timeInterval !== this.oldTimeInterval) {
      this.updateInterval();
    }

    if (hoverMode !== this.oldHoverMode) {
      this.onHoverModeUpdate();
    }

    if (
      selection !== this.oldSelection ||
      timeInterval !== this.oldTimeInterval ||
      timeHighlight !== this.oldTimeHighlight
    ) {
      this.draw();
    } else {
      this.updateCrosshair();
    }

    this.set('oldSelection', selection);
    this.set('oldTimeInterval', timeInterval);
    this.set('oldTimeHighlight', timeHighlight);
    this.set('oldHoverMode', hoverMode);
  },

  update() {
    this.updateTimeHighlight();
    this._super(...arguments);
  },

  draw() {
    this.updateCrosshair();
    this._super(...arguments);
  },

  updateCrosshair() {
    let { flot, time } = this;

    if (time === null) {
      flot.clearCrosshair();
    } else if (time === -1) {
      flot.lockCrosshair({ x: 999999999 });
    } else {
      flot.lockCrosshair({ x: time * 1000 });
    }
  },

  updateInterval() {
    let { flot, timeInterval: interval } = this;
    let opt = flot.getOptions();

    if (!interval) {
      opt.xaxes[0].min = opt.xaxes[0].max = null;
    } else {
      let [start, end] = interval;
      opt.xaxes[0].min = start * 1000;
      opt.xaxes[0].max = end * 1000;
    }
  },

  onHoverModeUpdate() {
    let placeholder = this.placeholder;

    if (this.hoverMode) {
      placeholder.on('plothover', (event, pos) => {
        this.set('time', pos.x / 1000);
      });

      placeholder.on('mouseout', () => {
        this.set('time', this.defaultTime);
      });
    } else {
      placeholder.off('plothover');
      placeholder.off('mouseout');
    }
  },

  updateTimeHighlight() {
    // There is no flot.setOptions(), so we modify them in-place.
    let options = this.flot.getOptions();

    // Clear the markings if there is no time highlight
    let time_highlight = this.timeHighlight;
    if (!time_highlight) {
      options.grid.markings = [];
      return;
    }

    // Add time highlight as flot markings
    options.grid.markings = [
      {
        color: '#fff083',
        xaxis: {
          from: time_highlight.start * 1000,
          to: time_highlight.end * 1000,
        },
      },
    ];
  },
});
