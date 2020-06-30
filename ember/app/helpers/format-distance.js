import Helper from '@ember/component/helper';
import { inject as service } from '@ember/service';

export default Helper.extend({
  units: service(),

  compute([value], options) {
    return this.units.formatDistance(value, options);
  },
});
