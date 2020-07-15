import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { equal, alias, readOnly } from '@ember/object/computed';

import isNone from '../computed/is-none';

export default class UploadResultForm extends Component {
  tagName = '';

  result = null;
  clubMembers = null;
  aircraftModels = null;

  @readOnly('result.status') status;
  @alias('result.flight') flight;
  @alias('result.trace') trace;
  @readOnly('result.airspaces') airspaces;

  @alias('flight.pilotId') pilotId;
  @alias('flight.pilotName') pilotName;
  @isNone('pilotId') showPilotNameInput;

  @alias('flight.copilotId') copilotId;
  @alias('flight.copilotName') copilotName;
  @isNone('copilotId') showCopilotNameInput;

  @alias('flight.modelId') modelId;
  @alias('flight.registration') registration;
  @alias('flight.competitionId') competitionId;

  @computedDate('trace.igc_start_time') igcStartTime;
  @computedDate('flight.takeoffTime') takeoffTime;
  @computedDate('flight.scoreStartTime') scoreStartTime;
  @computedDate('flight.scoreEndTime') scoreEndTime;
  @computedDate('flight.landingTime') landingTime;
  @computedDate('trace.igc_end_time') igcEndTime;

  @equal('status', 0) success;
  @readOnly('result.validations') validations;

  @action
  setTakeoffTime(value) {
    this.set('takeoffTime', value);

    let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
    if (times.takeoffTime > times.scoreStartTime) {
      this.set('scoreStartTime', times.takeoffTime);
    }
    if (times.takeoffTime > times.scoreEndTime) {
      this.set('scoreEndTime', times.takeoffTime);
    }
    if (times.takeoffTime > times.landingTime) {
      this.set('landingTime', times.takeoffTime);
    }
  }

  @action
  setScoreStartTime(value) {
    this.set('scoreStartTime', value);

    let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
    if (times.scoreStartTime < times.takeoffTime) {
      this.set('takeoffTime', times.scoreStartTime);
    }
    if (times.scoreStartTime > times.scoreEndTime) {
      this.set('scoreEndTime', times.scoreStartTime);
    }
    if (times.scoreStartTime > times.landingTime) {
      this.set('landingTime', times.scoreStartTime);
    }
  }

  @action
  setScoreEndTime(value) {
    this.set('scoreEndTime', value);

    let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
    if (times.scoreEndTime < times.takeoffTime) {
      this.set('takeoffTime', times.scoreEndTime);
    }
    if (times.scoreEndTime < times.scoreStartTime) {
      this.set('scoreStartTime', times.scoreEndTime);
    }
    if (times.scoreEndTime > times.landingTime) {
      this.set('landingTime', times.scoreEndTime);
    }
  }

  @action
  setLandingTime(value) {
    this.set('landingTime', value);

    let times = this.getProperties('takeoffTime', 'scoreStartTime', 'scoreEndTime', 'landingTime');
    if (times.landingTime < times.takeoffTime) {
      this.set('takeoffTime', times.landingTime);
    }
    if (times.landingTime < times.scoreStartTime) {
      this.set('scoreStartTime', times.landingTime);
    }
    if (times.landingTime < times.scoreEndTime) {
      this.set('scoreEndTime', times.landingTime);
    }
  }
}

/**
 * Converts from ISO 8601 strings to Date instances and vice-versa.
 */
function computedDate(aliasKey) {
  return computed(aliasKey, {
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
