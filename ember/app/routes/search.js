import { action } from '@ember/object';
import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class SearchRoute extends Route {
  @service ajax;
  @service('searchText') searchTextService;

  queryParams = {
    text: {
      refreshModel: true,
    },
  };

  model(params) {
    let searchText = params.text;
    this.set('searchTextService.text', searchText);

    if (searchText) {
      return this.ajax.request(`/api/search?text=${searchText}`);
    }
  }

  @action
  loading(transition) {
    let controller = this.controllerFor('search');
    controller.set('currentlyLoading', true);
    transition.promise.finally(() => {
      controller.set('currentlyLoading', false);
    });
    return true;
  }

  deactivate() {
    this.set('searchTextService.text', null);
  }
}
