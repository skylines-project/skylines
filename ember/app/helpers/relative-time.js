import { selectUnit } from '@formatjs/intl-utils';
import { task, rawTimeout } from 'ember-concurrency';
import BaseHelper from 'ember-intl/-private/helpers/-format-base';

const UPDATE_INTERVALS = {
  second: 500,
  minute: 15 * 1000,
  hour: 10 * 60 * 1000,
  day: 4 * 60 * 60 * 1000,
};

export default class extends BaseHelper {
  format(date) {
    let { value, unit } = selectUnit(date);

    let updateInterval = UPDATE_INTERVALS[unit];
    if (updateInterval !== undefined) {
      this.updateTask.perform(updateInterval);
    }

    return this.intl.formatRelative(value, { unit });
  }

  @(task(function* (interval) {
    yield rawTimeout(interval);
    this.recompute();
  }).restartable())
  updateTask;
}
