import Ember from 'ember';

import isNone from '../computed/is-none';

export default Ember.Component.extend({
  classNames: ['row'],

  result: null,
  clubMembers: null,
  aircraftModels: null,

  status: Ember.computed.readOnly('result.status'),
  flight: Ember.computed.alias('result.flight'),
  trace: Ember.computed.alias('result.trace'),
  airspaces: Ember.computed.readOnly('result.airspaces'),

  pilotId: Ember.computed.alias('flight.pilotId'),
  pilotName: Ember.computed.alias('flight.pilotName'),
  showPilotNameInput: isNone('pilotId'),

  copilotId: Ember.computed.alias('flight.copilotId'),
  copilotName: Ember.computed.alias('flight.copilotName'),
  showCopilotNameInput: isNone('copilotId'),

  modelId: Ember.computed.alias('flight.modelId'),
  registration: Ember.computed.alias('flight.registration'),
  competitionId: Ember.computed.alias('flight.competitionId'),

  igcStartTime: computedDate('trace.igc_start_time'),
  takeoffTime: computedDate('flight.takeoffTime'),
  scoreStartTime: computedDate('flight.scoreStartTime'),
  scoreEndTime: computedDate('flight.scoreEndTime'),
  landingTime: computedDate('flight.landingTime'),
  igcEndTime: computedDate('trace.igc_end_time'),

  success: Ember.computed.equal('status', 0),
  validations: Ember.computed.readOnly('result.validations'),

  actions: {
    setTakeoffTime(value) {
      this.set('takeoffTime', value);

      let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
      if (times.takeoffTime > times.scoreStartTime) { this.set('scoreStartTime', times.takeoffTime); }
      if (times.takeoffTime > times.scoreEndTime) { this.set('scoreEndTime', times.takeoffTime); }
      if (times.takeoffTime > times.landingTime) { this.set('landingTime', times.takeoffTime); }
    },

    setScoreStartTime(value) {
      this.set('scoreStartTime', value);

      let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
      if (times.scoreStartTime < times.takeoffTime) { this.set('takeoffTime', times.scoreStartTime); }
      if (times.scoreStartTime > times.scoreEndTime) { this.set('scoreEndTime', times.scoreStartTime); }
      if (times.scoreStartTime > times.landingTime) { this.set('landingTime', times.scoreStartTime); }
    },

    setScoreEndTime(value) {
      this.set('scoreEndTime', value);

      let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
      if (times.scoreEndTime < times.takeoffTime) { this.set('takeoffTime', times.scoreEndTime); }
      if (times.scoreEndTime < times.scoreStartTime) { this.set('scoreStartTime', times.scoreEndTime); }
      if (times.scoreEndTime > times.landingTime) { this.set('landingTime', times.scoreEndTime); }
    },

    setLandingTime(value) {
      this.set('landingTime', value);

      let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
      if (times.landingTime < times.takeoffTime) { this.set('takeoffTime', times.landingTime); }
      if (times.landingTime < times.scoreStartTime) { this.set('scoreStartTime', times.landingTime); }
      if (times.landingTime < times.scoreEndTime) { this.set('scoreEndTime', times.landingTime); }
    },
  },
});

/**
 * Converts from ISO 8601 strings to Date instances and vice-versa.
 */
function computedDate(aliasKey) {
  return Ember.computed(aliasKey, {
    get() {
      let str = this.get(aliasKey);
      if (str) {
        return new Date(str);
      }
    },
    set(key, value) {
      let date = value ? value.toISOString() : value;
      this.set(aliasKey, date);
      return value;
    },
  });
}
