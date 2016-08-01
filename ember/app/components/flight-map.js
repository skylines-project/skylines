import Ember from 'ember';

import BaseMapComponent from './base-map';

export default BaseMapComponent.extend({
  fixCalc: Ember.inject.service(),

  flights: Ember.computed.readOnly('fixCalc.flights'),

  actions: {
    cesiumEnabled() {
      this.set('cesiumEnabled', true);
    },
    cesiumDisabled() {
      this.set('cesiumEnabled', false);
    },
  },
});
