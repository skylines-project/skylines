import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  queryParams: {
    page: { refreshModel: true },
    column: { refreshModel: true },
    order: { refreshModel: true },
  },

  model(params) {
    return this.get('ajax').request(this.getURL(params), {
      data: {
        page: params.page,
        column: params.column,
        order: params.order,
      },
    });
  },

  getURL(/* params */) {
    throw new Error('Not implemented: `getURL`');
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
});
