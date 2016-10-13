import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel', 'panel-default'],

  callsign: null,
  delay: null,
  messageKey: null,
  error: null,

  delays: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 45, 60],

  /* ember-power-select can't handle `0` */
  _delay: Ember.computed('delay', function() {
    let delay = this.get('delay');
    return (delay === 0) ? '0' : delay;
  }),

  saveTask: task(function * () {
    let json = {
      trackingCallsign: this.get('callsign'),
      trackingDelay: this.get('delay'),
    };

    try {
      yield this.get('ajax').request('/settings/', { method: 'POST', json });

      this.setProperties({
        messageKey: 'settings-have-been-saved',
        error: null,
      });

    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.get('saveTask').perform();
        }
      });
    },
  },
});
