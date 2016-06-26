import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

import { PRESETS } from '../../utils/units';

const Validations = buildValidations({
  email: {
    descriptionKey: 'email-address',
    validators: [
      validator('presence', true),
      validator('format', { type: 'email' }),
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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel', 'panel-default'],

  email: null,
  firstName: null,
  lastName: null,
  distanceUnitIndex: null,
  speedUnitIndex: null,
  liftUnitIndex: null,
  altitudeUnitIndex: null,

  pending: false,
  messageKey: null,
  error: null,

  distanceUnits: ['m', 'km', 'NM', 'mi'],
  speedUnits: ['m/s', 'km/h', 'kt', 'mph'],
  liftUnits: ['m/s', 'kt', 'ft/min'],
  altitudeUnits: ['m', 'ft'],

  distanceUnit: computedUnit('distanceUnits', 'distanceUnitIndex'),
  speedUnit: computedUnit('speedUnits', 'speedUnitIndex'),
  liftUnit: computedUnit('liftUnits', 'liftUnitIndex'),
  altitudeUnit: computedUnit('altitudeUnits', 'altitudeUnitIndex'),

  unitsPresets: ['custom', 'european', 'british', 'australian', 'american'],

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

  sendChangeRequest() {
    let json = this.getProperties([
      'email',
      'firstName',
      'lastName',
      'distanceUnitIndex',
      'speedUnitIndex',
      'liftUnitIndex',
      'altitudeUnitIndex',
    ]);

    this.set('pending', true);
    this.get('ajax').request('/settings/profile', { method: 'POST', json }).then(() => {
      this.setProperties({
        messageKey: 'settings-have-been-saved',
        error: null,
      });
    }).catch(error => {
      this.setProperties({ messageKey: null, error });
    }).finally(() => {
      this.set('pending', false);
    });
  },

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.sendChangeRequest();
        }
      });
    },
  },
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
  })
}
