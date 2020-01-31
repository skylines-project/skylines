import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  queryParams: {
    page: { refreshModel: true },
    year: ['year'],
  },

  year: new Date().getFullYear().toString(),

  model(params) {
    let data = {
      year: params.year,
      page: params.page,
    };

    return this.ajax.request('/api/clubs', { data });
  },

  setupController(controller) {
    this._super(...arguments);
    controller.set('year', this.year);
  },

  resetController(controller, isExiting) {
    this._super(...arguments);
    if (isExiting) {
      controller.set('page', 1);
    }
  },

  actions: {
    loading(transition) {
      let controller = this.controllerFor('clubs');
      controller.set('loading', true);
      transition.promise.finally(() => {
        controller.set('loading', false);
      });
    },
  },
});
