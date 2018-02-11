import Controller from '@ember/controller';

export default Controller.extend({
  actions: {
    transitionTo(...args) {
      this.transitionToRoute(...args);
    },
  },
});
