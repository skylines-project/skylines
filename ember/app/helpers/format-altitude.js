import Ember from 'ember';

import { formatAltitude } from '../utils/units';

export default Ember.Helper.extend({
  compute([value], options) {
    return formatAltitude(value, options);
  },
});
