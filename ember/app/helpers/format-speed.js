import Ember from 'ember';

export default Ember.Helper.extend({
  units: Ember.inject.service(),

  speedUnitObserver: Ember.observer('units.speedUnit', function() {
    this.recompute();
  }),

  compute([value], options) {
    return this.get('units').formatSpeed(value, options);
  },
});
