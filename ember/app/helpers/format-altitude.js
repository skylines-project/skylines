import Helper from '@ember/component/helper';
import { observer } from '@ember/object';
import { inject as service } from '@ember/service';

export default Helper.extend({
  units: service(),

  altitudeUnitObserver: observer('units.altitudeUnit', function() {
    this.recompute();
  }),

  compute([value], options) {
    return this.units.formatAltitude(value, options);
  },
});
