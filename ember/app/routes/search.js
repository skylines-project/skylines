import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
  ajax: service(),
  searchTextService: service('searchText'),

  queryParams: {
    text: {
      refreshModel: true,
    },
  },

  model(params, transition) {
    let searchText = transition.queryParams && transition.queryParams.text;
    this.set('searchTextService.text', searchText);

    if (searchText) {
      return this.get('ajax').request(`/api/search?text=${searchText}`);
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

  deactive() {
    this._super(...arguments);
    this.set('searchTextService.text', null);
  },
});
