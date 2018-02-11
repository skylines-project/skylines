import { mapBy, max, sum } from '@ember/object/computed';
import Component from '@ember/component';

export default Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,

  distances: mapBy('years', 'distance'),
  max: max('distances'),
  sum: sum('distances'),
});
