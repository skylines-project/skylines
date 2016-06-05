import Ember from 'ember';

export default Ember.Service.extend({
  selection: null,

  init() {
    this._super(...arguments);
    window.flightPhaseService = this;
  },
});
