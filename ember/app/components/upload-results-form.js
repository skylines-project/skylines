import Ember from 'ember';
import { task } from 'ember-concurrency';

import UploadResult from '../utils/upload-result';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),

  results: null,
  clubMembers: null,
  aircraftModels: null,

  successfulResults: Ember.computed.filterBy('validatedResults', 'success', true),
  success: Ember.computed.notEmpty('successfulResults'),

  validations: Ember.computed.mapBy('successfulResults', 'validations'),

  invalidValidations: Ember.computed.filterBy('validations', 'isValid', false),
  isInvalid: Ember.computed.notEmpty('invalidValidations'),

  didReceiveAttrs() {
    this._super(...arguments);

    let ownerInjection = Ember.getOwner(this).ownerInjection();
    this.set('validatedResults', this.get('results').map(_result => {
      let result = UploadResult.create(ownerInjection, _result);

      if (result.get('flight')) {
        result.set('pilotId', result.get('flight.pilot.id'));
        result.set('copilotId', result.get('flight.copilot.id'));
        result.set('modelId', result.get('flight.model.id'));
      }

      return result;
    }));
  },

  saveTask: task(function * () {
    let json = this.get('successfulResults').map(result => {
      let flight = Ember.get(result, 'flight');
      return Ember.getProperties(flight, 'id', 'pilotId', 'pilotName', 'copilotId', 'copilotName',
        'modelId', 'registration', 'competitionId', 'takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
    });

    try {
      yield this.get('ajax').request('/api/flights/upload/verify', { method: 'POST', json });
      let ids = json.map(flight => flight.id);
      if (ids.length === 1) {
        this.getWithDefault('transitionTo')('flight', ids[0]);
      } else {
        this.getWithDefault('transitionTo')('flights.list', ids.join(','));
      }

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
