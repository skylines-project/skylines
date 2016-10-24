import Ember from 'ember';

export default Ember.Controller.extend({
  actions: {
    transitionTo(...args) {
      this.transitionToRoute(...args);
    },
  },
});
