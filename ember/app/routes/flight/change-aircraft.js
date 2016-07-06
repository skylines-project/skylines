import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model() {
    let id = this.modelFor('flight').ids[0];

    let flight = this.get('ajax').request(`/flights/${id}/`).then(it => it.flight);
    let aircraftModels = this.get('ajax').request('/aircraft-models').then(it => it.models);

    return Ember.RSVP.hash({ id, flight, aircraftModels });
  },
});
