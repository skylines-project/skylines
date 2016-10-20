import Ember from 'ember';

export default Ember.Helper.extend({
  units: Ember.inject.service(),

  altitudeUnitObserver: Ember.observer('units.altitudeUnit', function() {
    this.recompute();
  }),

  compute([value], options) {
    return this.get('units').formatAltitude(value, options);
  },
});
