import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';
import { conditional, eq } from 'ember-awesome-macros';
import raw from 'ember-macro-helpers/raw';

const Validations = buildValidations({
  callsign: {
    descriptionKey: 'tracking-callsign',
    validators: [
      validator('presence', true),
      validator('length', { max: 5 }),
    ],
    debounce: 500,
  },
});

const DELAYS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 45, 60];

export default Component.extend(Validations, {
  ajax: service(),

  classNames: ['panel', 'panel-default'],

  callsign: null,
  delay: null,
  messageKey: null,
  error: null,

  delays: DELAYS,

  /* ember-power-select can't handle `0` */
  _delay: conditional(eq('delay', 0), raw('0'), 'delay'),

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.get('saveTask').perform();
      }
    },
  },

  saveTask: task(function * () {
    let json = {
      trackingCallsign: this.get('callsign'),
      trackingDelay: this.get('delay'),
    };

    try {
      yield this.get('ajax').request('/api/settings/', { method: 'POST', json });

      this.setProperties({
        messageKey: 'settings-have-been-saved',
        error: null,
      });

    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});
