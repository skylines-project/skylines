import { get } from '@ember/object';
import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
  ajax: service(),

  model(params) {
    return this.get('ajax').request(this.getURL(params));
  },

  setupController(controller, model) {
    this._super(...arguments);

    let routeName = this.get('routeName');
    let params = this.paramsFor(routeName);

    this.controllerFor('statistics').setProperties({
      airport: (routeName === 'statistics.airport') ? parseInt(params.airport_id, 10) : null,
      pilot: (routeName === 'statistics.pilot') ? parseInt(params.pilot_id, 10) : null,
      club: (routeName === 'statistics.club') ? parseInt(params.club_id, 10) : null,
      name: get(model, 'name'),
    });
  },

  getURL(/* params */) {
    throw new Error('Not implemented: `getURL`');
  },
});
