import Controller from '@ember/controller';

export default Controller.extend({
  queryParams: ['baselayer', 'overlays'],
  baselayer: null,
  overlays: null,

  actions: {
    transitionTo(...args) {
      this.transitionToRoute(...args);
    },
  },
});
