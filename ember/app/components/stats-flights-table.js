import { mapBy, max, sum } from '@ember/object/computed';
import Component from '@ember/component';

export default Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,

  flights: mapBy('years', 'flights'),
  max: max('flights'),
  sum: sum('flights'),
});
