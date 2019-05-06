import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  queryParams: {
    page: { refreshModel: true },
    column: { refreshModel: true },
    order: { refreshModel: true },
  },

  model(params) {
    return this.ajax.request(this.getURL(params), {
      data: {
        page: params.page,
        column: params.column,
        order: params.order,
      },
    });
  },

  resetController(controller, isExiting) {
    this._super(...arguments);
    if (isExiting) {
      controller.set('page', 1);
    }
  },

  actions: {
    loading(transition) {
      let controller = this.controllerFor('flights');
      controller.set('loading', true);
      transition.promise.finally(() => {
        controller.set('loading', false);
      });
    },
  },

  getURL(/* params */) {
    throw new Error('Not implemented: `getURL`');
  },
});
