import Ember from 'ember';
import RSVP from 'rsvp';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model() {
    let id = this.modelFor('flight').ids[0];

    let flight = this.get('ajax').request(`/api/flights/${id}/`).then(it => it.flight);
    let aircraftModels = this.get('ajax').request('/api/aircraft-models').then(it => it.models);

    return RSVP.hash({ id, flight, aircraftModels });
  },
});
