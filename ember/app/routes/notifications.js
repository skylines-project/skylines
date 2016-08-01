import Ember from 'ember';
import { UnauthorizedError } from 'ember-ajax/errors';

const PER_PAGE = 20;

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  queryParams: {
    page: { refreshModel: true },
    user: { refreshModel: true },
    type: { refreshModel: true },
  },

  model(params) {
    let data = {
      page: params.page,
      per_page: PER_PAGE,
    };

    if (params.user) {
      data.user = params.user;
    }

    if (params.type) {
      data.type = params.type;
    }

    return this.get('ajax').request('/notifications', { data });
  },

  setupController(controller) {
    this._super(...arguments);
    controller.set('perPage', PER_PAGE);
  },

  resetController(controller, isExiting) {
    this._super(...arguments);
    if (isExiting) {
      controller.set('page', 1);
      controller.set('user', null);
      controller.set('type', null);
    }
  },

  actions: {
    loading(transition) {
      let controller = this.controllerFor('notifications');
      controller.set('loading', true);
      transition.promise.finally(() => {
        controller.set('loading', false);
      });
    },

    error(error) {
      if (error instanceof UnauthorizedError) {
        window.location = `/login?next=${encodeURI(window.location)}`;
      }
    },

    markAsRead() {
      let controller = this.controllerFor('notifications');
      controller.set('clearing', true);
      this.get('ajax').request('/notifications/clear', { method: 'POST' }).then(() => {
        controller.get('model.events').forEach(event => Ember.set(event, 'unread', false));
      }).finally(() => {
        controller.set('clearing', false);
      });
    },
  },
});
