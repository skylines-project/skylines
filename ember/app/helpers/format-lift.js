import Helper from '@ember/component/helper';
import { observer } from '@ember/object';
import { inject as service } from '@ember/service';

export default Helper.extend({
  units: service(),

  liftUnitObserver: observer('units.liftUnit', function() {
    this.recompute();
  }),

  compute([value], options) {
    return this.units.formatLift(value, options);
  },
});
