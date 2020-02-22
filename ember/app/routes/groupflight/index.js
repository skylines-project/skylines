import Route from '@ember/routing/route';

export default Route.extend({
    afterModel() {
      this.transitionTo('flight', this.modelFor('groupflight').ids.join(','));
    }
});

