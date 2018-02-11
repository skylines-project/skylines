import Controller from '@ember/controller';

export default Controller.extend({
  actions: {
    transitionToFlight() {
      this.transitionToRoute('flight', this.get('model.id'));
    },
  },
});
