import Ember from 'ember';

export default Ember.Helper.extend({
  units: Ember.inject.service(),

  liftUnitObserver: Ember.observer('units.liftUnit', function() {
    this.recompute();
  }),

  compute([value], options) {
    return this.get('units').formatLift(value, options);
  },
});
