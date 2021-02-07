import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

const PER_PAGE = 20;

export default Route.extend({
  ajax: service(),
  session: service(),

  queryParams: {
    page: { refreshModel: true },
    user: { refreshModel: true },
    type: { refreshModel: true },
  },

  beforeModel(transition) {
    this.session.requireAuthentication(transition, 'login');
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

    return this.ajax.request('/api/notifications', { data });
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
      return true;
    },
  },
});
