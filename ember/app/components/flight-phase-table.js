/* globals slUnits */

import Ember from 'ember';

export default Ember.Component.extend({
  init() {
    this._super(...arguments);

    this.set('altitudeUnit', slUnits.getAltitudeUnit());
    this.set('distanceUnit', slUnits.getDistanceUnit());
    this.set('liftUnit', slUnits.getLiftUnit());
    this.set('speedUnit', slUnits.getSpeedUnit());
  },
});
