import Ember from 'ember';

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

  sendChangeRequest() {
    let json = this.get('successfulResults').map(result => {
      let flight = Ember.get(result, 'flight');
      return Ember.getProperties(flight, 'id', 'pilotId', 'pilotName', 'copilotId', 'copilotName',
        'modelId', 'registration', 'competitionId', 'takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
    });

    this.set('pending', true);
    this.get('ajax').request('/flights/upload/verify', { method: 'POST', json }).then(() => {
      let ids = json.map(flight => flight.id);
      window.location = (ids.length === 1) ? `/flights/${ids[0]}/` : `/flights/list/${ids.join(',')}`;

    }).catch(error => {
      this.set('error', error);

    }).finally(() => {
      this.set('pending', false);
    });
  },

  actions: {
    submit() {
      let validates = this.get('validations').map(v => v.validate());

      Ember.RSVP.all(validates).then(results => {
        if (results.every(r => r.validations.get('isValid'))) {
          this.sendChangeRequest();
        }
      });
    },
  },
});
