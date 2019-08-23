import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),
  searchTextService: service('searchText'),

  queryParams: {
    text: {
      refreshModel: true,
    },
  },

  model(params) {
    let searchText = params.text;
    this.set('searchTextService.text', searchText);

    if (searchText) {
      return this.ajax.request(`/api/search?text=${searchText}`);
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
