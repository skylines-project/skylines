import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  callsign: {
    descriptionKey: 'tracking-callsign',
    validators: [validator('presence', true), validator('length', { max: 5 })],
    debounce: 500,
  },
});

const DELAYS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 45, 60];

export default Component.extend(Validations, {
  tagName: '',

  ajax: service(),

  callsign: null,
  delay: null,
  messageKey: null,
  error: null,

  delays: DELAYS,

  /* ember-power-select can't handle `0` */
  _delay: computed('delay', function() {
    return this.delay === 0 ? '0' : this.delay;
  }),

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.saveTask.perform();
      }
    },
  },

  saveTask: task(function*() {
    let json = {
      trackingCallsign: this.callsign,
      trackingDelay: this.delay,
    };

    try {
      yield this.ajax.request('/api/settings/', { method: 'POST', json });

      this.setProperties({
        messageKey: 'settings-have-been-saved',
        error: null,
      });
    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});
