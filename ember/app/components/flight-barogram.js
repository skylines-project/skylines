import Ember from 'ember';

import BarogramComponent from './base-barogram';

import safeComputed from '../utils/safe-computed';

export default BarogramComponent.extend({
  fixCalc: Ember.inject.service(),
  flightPhase: Ember.inject.service(),

  time: Ember.computed.alias('fixCalc.time'),

  timeObserver: Ember.observer('time', function() {
    Ember.run.once(this, 'updateCrosshair');
  }),

  flights: Ember.computed.readOnly('fixCalc.flights'),

  activeFlights: Ember.computed('flights.[]', 'selection', function() {
    let { flights, selection } = this.getProperties('flights', 'selection');
    return flights.filter(flight => (!selection || flight.get('id') === selection));
  }),

  passiveFlights: Ember.computed('flights.[]', 'selection', function() {
    let { flights, selection } = this.getProperties('flights', 'selection');
    return flights.filter(flight => (selection && flight.get('id') !== selection));
  }),

  active: Ember.computed('activeFlights.@each.{flot_h,color}', function() {
    return this.get('activeFlights').map(flight => ({
      data: flight.get('flot_h'),
      color: flight.get('color'),
    }));
  }),

  passive: Ember.computed('passiveFlights.@each.{flot_h,color}', function() {
    return this.get('passiveFlights').map(flight => ({
      data: flight.get('flot_h'),
      color: flight.get('color'),
    }));
  }),

  enls: Ember.computed('activeFlights.@each.{flot_enl,color}', function() {
    return this.get('activeFlights').map(flight => ({
      data: flight.get('flot_enl'),
      color: flight.get('color'),
    }));
  }),

  selectedFlight: Ember.computed('flights.[]', 'selection', function() {
    let { flights, selection } = this.getProperties('flights', 'selection');
    if (flights.get('length') === 1) {
      return flights.get('firstObject');
    } else if (selection) {
      return flights.findBy('id', selection);
    }
  }),

  contests: safeComputed('selectedFlight', flight => flight.get('contests')),
  elevations: safeComputed('selectedFlight', flight => flight.get('flot_elev')),

  timeHighlight: Ember.computed.readOnly('flightPhase.selection'),

  hoverMode: Ember.computed.not('fixCalc.isRunning'),
  hoverModeObserver: Ember.observer('hoverMode', function() {
    Ember.run.once(this, 'onHoverModeUpdate');
  }),

  timeInterval: null,
  timeIntervalObserver: Ember.observer('timeInterval', function() {
    this.updateInterval();
  }),

  init() {
    this._super(...arguments);
    window.barogram = this;
  },

  didInsertElement() {
    this._super(...arguments);
    this.onHoverModeUpdate();
  },

  draw() {
    this.updateCrosshair();
    this._super(...arguments);
  },

  updateCrosshair() {
    let { flot, time } = this.getProperties('flot', 'time');

    if (time === null) {
      flot.clearCrosshair();
    } else if (time == -1) {
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
});
