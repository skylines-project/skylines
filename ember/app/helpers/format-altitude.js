import { observer } from '@ember/object';
import { inject as service } from '@ember/service';
import Helper from '@ember/component/helper';

export default Helper.extend({
  units: service(),

  altitudeUnitObserver: observer('units.altitudeUnit', function() {
    this.recompute();
  }),

  compute([value], options) {
    return this.get('units').formatAltitude(value, options);
  },
});
