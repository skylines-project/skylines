import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),
  searchTextService: Ember.inject.service('searchText'),

  queryParams: {
    text: {
      refreshModel: true,
    },
  },

  model(params, transition) {
    let searchText = transition.queryParams && transition.queryParams.text;
    this.set('searchTextService.text', searchText);

    if (searchText) {
      return this.get('ajax').request(`/search/?text=${searchText}`);
    }
  },

  deactive() {
    this._super(...arguments);
    this.set('searchTextService.text', null);
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
