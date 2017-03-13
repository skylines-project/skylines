import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

import { PRESETS } from '../../services/units';

const Validations = buildValidations({
  email: {
    descriptionKey: 'email-address',
    validators: [
      validator('presence', true),
      validator('format', { type: 'email' }),
      validator('unique-email', { messageKey: 'email-exists-already' }),
    ],
    debounce: 500,
  },
  firstName: {
    descriptionKey: 'first-name',
    validators: [
      validator('presence', true),
    ],
    debounce: 500,
  },
  lastName: {
    descriptionKey: 'last-name',
    validators: [
      validator('presence', true),
    ],
    debounce: 500,
  },
});

const PRESET_NAMES = ['custom', 'european', 'british', 'australian', 'american'];

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),
  units: Ember.inject.service(),

  classNames: ['panel', 'panel-default'],

  unitsPresets: PRESET_NAMES,

  email: null,
  firstName: null,
  lastName: null,
  distanceUnitIndex: null,
  speedUnitIndex: null,
  liftUnitIndex: null,
  altitudeUnitIndex: null,

  messageKey: null,
  error: null,

  distanceUnit: computedUnit('units.distanceUnits', 'distanceUnitIndex'),
  speedUnit: computedUnit('units.speedUnits', 'speedUnitIndex'),
  liftUnit: computedUnit('units.liftUnits', 'liftUnitIndex'),
  altitudeUnit: computedUnit('units.altitudeUnits', 'altitudeUnitIndex'),

  unitsPreset: Ember.computed('distanceUnit', 'speedUnit', 'liftUnit', 'altitudeUnit', {
    get() {
      let units = this.getProperties('distanceUnit', 'speedUnit', 'liftUnit', 'altitudeUnit');

      let matches = Object.keys(PRESETS).filter(key => {
        let preset = PRESETS[key];

        return preset.distance === units.distanceUnit &&
          preset.speed === units.speedUnit &&
          preset.lift === units.liftUnit &&
          preset.altitude === units.altitudeUnit;
      });

      return (matches.length > 0) ? matches[0] : 'custom';
    },

    set(key, value) {
      if (value !== 'custom') {
        let preset = PRESETS[value];
        this.setProperties({
          distanceUnit: preset.distance,
          speedUnit: preset.speed,
          liftUnit: preset.lift,
          altitudeUnit: preset.altitude,
        });
      }
      return value;
    },
  }),

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.get('saveTask').perform();
        }
      });
    },
  },

  saveTask: task(function * () {
    let json = {
      email: this.get('email'),
      firstName: this.get('firstName'),
      lastName: this.get('lastName'),
      distanceUnit: this.get('distanceUnitIndex'),
      speedUnit: this.get('speedUnitIndex'),
      liftUnit: this.get('liftUnitIndex'),
      altitudeUnit: this.get('altitudeUnitIndex'),
    };

    try {
      yield this.get('ajax').request('/api/settings/', { method: 'POST', json });
      this.setProperties({
        messageKey: 'settings-have-been-saved',
        error: null,
      });

      this.get('units').setProperties({
        altitudeUnit: this.get('altitudeUnit'),
        distanceUnit: this.get('distanceUnit'),
        liftUnit: this.get('liftUnit'),
        speedUnit: this.get('speedUnit'),
      });

    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});

function computedUnit(unitsKey, indexKey) {
  return Ember.computed(indexKey, {
    get() {
      return this.get(unitsKey)[this.get(indexKey)];
    },
    set(key, value) {
      this.set(indexKey, this.get(unitsKey).indexOf(value));
      return value;
    },
  });
}
