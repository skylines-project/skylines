import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  queryParams: {
    page: { refreshModel: true },
  },

  model(params) {
    let data = {
      year: this.paramsFor('ranking').year,
      page: params.page,
    };

    return this.get('ajax').request('/api/ranking/clubs', { data });
  },

  setupController(controller) {
    this._super(...arguments);
    controller.set('year', this.paramsFor('ranking').year);
  },

  resetController(controller, isExiting) {
    this._super(...arguments);
    if (isExiting) {
      controller.set('page', 1);
    }
  },

  actions: {
    loading(transition) {
      let controller = this.controllerFor('ranking');
      controller.set('loading', true);
      transition.promise.finally(() => {
        controller.set('loading', false);
      });
    },
  },
});
