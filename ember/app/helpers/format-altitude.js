import { inject as service } from '@ember/service';

import BaseHelper from 'ember-intl/-private/helpers/-format-base';

export default class extends BaseHelper {
  @service units;

  format(value, options) {
    return this.units.formatAltitude(value, options);
  }
}
