import Ember from 'ember';
import getNextSmallerIndex from '../utils/next-smaller-index';

export default Ember.Object.extend({
  fixCalc: null,
  selection: null,

  flight: Ember.computed.readOnly('fixCalc.flights.firstObject'),

  coordinates: Ember.computed('flight', 'selection.{start,end}', function() {
    let selection = this.get('selection');
    if (!selection) {
      return;
    }

    let { start, end } = selection;

    let flight = this.get('flight');
    let times = flight.get('time');

    let start_index = getNextSmallerIndex(times, start);
    let end_index = getNextSmallerIndex(times, end);
    if (start_index >= end_index) {
      return;
    }

    let coordinates = flight.get('geometry').getCoordinates();
    return coordinates.slice(start_index, end_index + 1);
  }),
});
