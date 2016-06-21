import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({wildcard}) {
    if (wildcard) {
      let data = wildcard.split('/');
      this.set('page', data[0]);
      this.set('id', parseInt(data[1], 10));
    } else {
      this.set('page', null);
      this.set('id', null);
    }

    return this.get('ajax').request(`/statistics/${wildcard}`);
  },

  setupController(controller) {
    this._super(...arguments);

    controller.set('pilot', null);
    controller.set('club', null);
    controller.set('airport', null);

    let page = this.get('page');
    let id = this.get('id');
    if (page && id) {
      controller.set(page, id);
    }
  },

  actions: {
    loading(transition) {
      let controller = this.controllerFor('stats.wildcard');
      controller.set('currentlyLoading', true);
      transition.promise.finally(() => {
        controller.set('currentlyLoading', false);
      });
    },
  },
});
