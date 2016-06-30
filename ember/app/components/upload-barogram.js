import Ember from 'ember';

import FlightBarogram from './flight-barogram';

export default FlightBarogram.extend({
  prefix: null,
  uploadMode: true,
  height: 160,

  init() {
    this._super(...arguments);
    window[`barogram-${this.get('prefix')}`] = this;
  },
});
