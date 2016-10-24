import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),

  results: null,
  clubMembers: null,
  aircraftModels: null,

  successfulResults: Ember.computed.filterBy('results', 'status', 0),
  success: Ember.computed.notEmpty('successfulResults'),

  validations: Ember.computed.mapBy('successfulResults', 'validations'),

  invalidValidations: Ember.computed.filterBy('validations', 'isValid', false),
  isInvalid: Ember.computed.notEmpty('invalidValidations'),

  saveTask: task(function * () {
    let json = this.get('successfulResults').map(result => {
      let flight = Ember.get(result, 'flight');
      return Ember.getProperties(flight, 'id', 'pilotId', 'pilotName', 'copilotId', 'copilotName',
        'modelId', 'registration', 'competitionId', 'takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
    });

    try {
      yield this.get('ajax').request('/api/flights/upload/verify', { method: 'POST', json });
      let ids = json.map(flight => flight.id);
      window.location = (ids.length === 1) ? `/flights/${ids[0]}/` : `/flights/list/${ids.join(',')}`;

    } catch (error) {
      this.set('error', error);
    }
  }).drop(),

  actions: {
    submit() {
      let validates = this.get('validations').map(v => v.validate());

      Ember.RSVP.all(validates).then(results => {
        if (results.every(r => r.validations.get('isValid'))) {
          this.get('saveTask').perform();
        }
      });
    },
  },
});
