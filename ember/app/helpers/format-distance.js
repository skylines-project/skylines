import Ember from 'ember';

import { formatDistance } from '../utils/units';

export default Ember.Helper.extend({
  compute([value], options) {
    return formatDistance(value, options);
  },
});
