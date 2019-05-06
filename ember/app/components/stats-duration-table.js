import Component from '@ember/component';
import { mapBy, max, sum } from '@ember/object/computed';

export default Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,

  durations: mapBy('years', 'duration'),
  max: max('durations'),
  sum: sum('durations'),
});
