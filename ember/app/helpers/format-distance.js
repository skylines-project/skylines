import Ember from 'ember';

export default Ember.Helper.extend({
  units: Ember.inject.service(),

  distanceUnitObserver: Ember.observer('units.distanceUnit', function() {
    this.recompute();
  }),

  compute([value], options) {
    return this.get('units').formatDistance(value, options);
  },
});
