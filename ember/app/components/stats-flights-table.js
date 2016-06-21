import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,

  flights: Ember.computed.mapBy('years', 'flights'),
  max: Ember.computed.max('flights'),
  sum: Ember.computed.sum('flights'),
});
