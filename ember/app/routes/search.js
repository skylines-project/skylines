import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  queryParams: {
    text: {
      refreshModel: true,
    },
  },

  model(params, transition) {
    let searchText = transition.queryParams && transition.queryParams.text;
    if (searchText) {
      return this.get('ajax').request(`/search/?text=${searchText}`);
    }
  },

  actions: {
    loading(transition) {
      let controller = this.controllerFor('search');
      controller.set('currentlyLoading', true);
      transition.promise.finally(() => {
        controller.set('currentlyLoading', false);
      });
    },
  },
});
