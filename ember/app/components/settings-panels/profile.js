import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

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
    validators: [validator('presence', true)],
    debounce: 500,
  },
  lastName: {
    descriptionKey: 'last-name',
    validators: [validator('presence', true)],
    debounce: 500,
  },
});

const PRESET_NAMES = ['custom', 'european', 'british', 'australian', 'american'];

export default Component.extend(Validations, {
  tagName: '',
  ajax: service(),
  units: service(),

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

  unitsPreset: computed('distanceUnit', 'speedUnit', 'liftUnit', 'altitudeUnit', {
    get() {
      let units = this.getProperties('distanceUnit', 'speedUnit', 'liftUnit', 'altitudeUnit');

      let matches = Object.keys(PRESETS).filter(key => {
        let preset = PRESETS[key];

        return (
          preset.distance === units.distanceUnit &&
          preset.speed === units.speedUnit &&
          preset.lift === units.liftUnit &&
          preset.altitude === units.altitudeUnit
        );
      });

      return matches.length > 0 ? matches[0] : 'custom';
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
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.saveTask.perform();
      }
    },
  },

  saveTask: task(function*() {
    let json = {
      email: this.email,
      firstName: this.firstName,
      lastName: this.lastName,
      distanceUnit: this.distanceUnitIndex,
      speedUnit: this.speedUnitIndex,
      liftUnit: this.liftUnitIndex,
      altitudeUnit: this.altitudeUnitIndex,
    };

    try {
      yield this.ajax.request('/api/settings/', { method: 'POST', json });
      this.setProperties({
        messageKey: 'settings-have-been-saved',
        error: null,
      });

      this.units.setProperties({
        altitudeUnit: this.altitudeUnit,
        distanceUnit: this.distanceUnit,
        liftUnit: this.liftUnit,
        speedUnit: this.speedUnit,
      });
    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});

function computedUnit(unitsKey, indexKey) {
  return computed(indexKey, {
    get() {
      return this.get(unitsKey)[this.get(indexKey)];
    },
    set(key, value) {
      this.set(indexKey, this.get(unitsKey).indexOf(value));
      return value;
    },
  });
}
