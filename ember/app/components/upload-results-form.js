import { getOwner } from '@ember/application';
import Component from '@ember/component';
import { get, getProperties } from '@ember/object';
import { filterBy, notEmpty, mapBy } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import RSVP from 'rsvp';

import UploadResult from '../utils/upload-result';

export default Component.extend({
  tagName: '',
  ajax: service(),

  results: null,
  clubMembers: null,
  aircraftModels: null,

  successfulResults: filterBy('validatedResults', 'success', true),
  success: notEmpty('successfulResults'),

  validations: mapBy('successfulResults', 'validations'),

  invalidValidations: filterBy('validations', 'isValid', false),
  isInvalid: notEmpty('invalidValidations'),

  didReceiveAttrs() {
    this._super(...arguments);

    let ownerInjection = getOwner(this).ownerInjection();
    this.set(
      'validatedResults',
      this.results.map(_result => {
        let result = UploadResult.create(ownerInjection, _result);

        if (result.get('flight')) {
          result.set('pilotId', result.get('flight.pilot.id'));
          result.set('copilotId', result.get('flight.copilot.id'));
          result.set('modelId', result.get('flight.model.id'));
        }

        return result;
      }),
    );
  },

  actions: {
    async submit() {
      let validates = this.validations.map(v => v.validate());

      let results = await RSVP.all(validates);
      if (results.every(r => r.validations.get('isValid'))) {
        this.saveTask.perform();
      }
    },
  },

  saveTask: task(function*() {
    let json = this.successfulResults.map(result => {
      let flight = get(result, 'flight');
      return getProperties(
        flight,
        'id',
        'pilotId',
        'pilotName',
        'copilotId',
        'copilotName',
        'modelId',
        'registration',
        'competitionId',
        'takeoffTime',
        'scoreStartTime',
        'scoreEndTime',
        'landingTime',
      );
    });

    try {
      yield this.ajax.request('/api/flights/upload/verify', { method: 'POST', json });
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
});
