import EmberObject, { computed } from '@ember/object';
import { readOnly } from '@ember/object/computed';

import getNextSmallerIndex from '../utils/next-smaller-index';

export default EmberObject.extend({
  fixCalc: null,
  selection: null,

  flight: readOnly('fixCalc.flights.firstObject'),

  coordinates: computed('flight', 'selection.{start,end}', function() {
    let selection = this.selection;
    if (!selection) {
      return;
    }

    let { start, end } = selection;

    let flight = this.flight;
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
