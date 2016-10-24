import Ember from 'ember';

export default Ember.Controller.extend({
  actions: {
    transitionToFlight() {
      this.transitionToRoute('flight', this.get('model.id'));
    },
  },
});
