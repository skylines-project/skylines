import Component from '@ember/component';
import { mapBy, max, sum } from '@ember/object/computed';

export default Component.extend({
  tagName: '',
  years: null,

  distances: mapBy('years', 'distance'),
  max: max('distances'),
  sum: sum('distances'),
});
