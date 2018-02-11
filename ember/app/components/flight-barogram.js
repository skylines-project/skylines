import { observer, computed } from '@ember/object';
import { conditional, eq } from 'ember-awesome-macros';
import { findBy } from 'ember-awesome-macros/array';
import raw from 'ember-macro-helpers/raw';

import BarogramComponent from './base-barogram';

import safeComputed from '../computed/safe-computed';

export default BarogramComponent.extend({
  flights: null,
  time: null,
  defaultTime: null,

  flightsObserver: observer('flights.[]', function() {
    this.draw();
  }),

  selection: null,

  activeFlights: computed('flights.[]', 'selection', function() {
    let { flights, selection } = this.getProperties('flights', 'selection');
    return flights.filter(flight => (!selection || flight.get('id') === selection));
  }),

  passiveFlights: computed('flights.[]', 'selection', function() {
    let { flights, selection } = this.getProperties('flights', 'selection');
    return flights.filter(flight => (selection && flight.get('id') !== selection));
  }),

  active: computed('activeFlights.@each.{flot_h,color}', function() {
    return this.get('activeFlights').map(flight => ({
      data: flight.get('flot_h'),
      color: flight.get('color'),
    }));
  }),

  passive: computed('passiveFlights.@each.{flot_h,color}', function() {
    return this.get('passiveFlights').map(flight => ({
      data: flight.get('flot_h'),
      color: flight.get('color'),
    }));
  }),

  enls: computed('activeFlights.@each.{flot_enl,color}', function() {
    return this.get('activeFlights').map(flight => ({
      data: flight.get('flot_enl'),
      color: flight.get('color'),
    }));
  }),

  selectedFlight: conditional(eq('flights.length', 1), 'flights.firstObject',
    conditional('selection', findBy('flights', raw('id'), 'selection'))),

  contests: safeComputed('selectedFlight', flight => flight.get('contests')),
  elevations: safeComputed('selectedFlight', flight => flight.get('flot_elev')),

  timeInterval: null,

  didInsertElement() {
    this._super(...arguments);
    this.onHoverModeUpdate();

    this.get('placeholder').on('plotclick', (event, pos) => {
      this.set('time', pos.x / 1000);
    });
  },

  didUpdateAttrs() {
    this._super(...arguments);
    let selection = this.get('selection');
    let timeInterval = this.get('timeInterval');
    let timeHighlight = this.get('timeHighlight');
    let hoverMode = this.get('hoverMode');

    if (timeInterval !== this.get('oldTimeInterval')) {
      this.updateInterval();
    }

    if (hoverMode !== this.get('oldHoverMode')) {
      this.onHoverModeUpdate();
    }

    if (selection !== this.get('oldSelection') ||
      timeInterval !== this.get('oldTimeInterval') ||
      timeHighlight !== this.get('oldTimeHighlight')) {
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
    let { flot, time } = this.getProperties('flot', 'time');

    if (time === null) {
      flot.clearCrosshair();
    } else if (time === -1) {
      flot.lockCrosshair({ x: 999999999 });
    } else {
      flot.lockCrosshair({ x: time * 1000 });
    }
  },

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

  onHoverModeUpdate() {
    let placeholder = this.get('placeholder');

    if (this.get('hoverMode')) {
      placeholder.on('plothover', (event, pos) => {
        this.set('time', pos.x / 1000);
      });

      placeholder.on('mouseout', () => {
        this.set('time', this.get('defaultTime'));
      });
    } else {
      placeholder.off('plothover');
      placeholder.off('mouseout');
    }
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
});
