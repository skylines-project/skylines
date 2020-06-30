import { inject as service } from '@ember/service';

import BaseHelper from 'ember-intl/helpers/-format-base';

export default BaseHelper.extend({
  units: service(),

  format(value, options) {
    return this.units.formatSpeed(value, options);
  },
});
