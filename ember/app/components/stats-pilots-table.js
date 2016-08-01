import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,
  sumPilots: null,

  pilots: Ember.computed.mapBy('years', 'pilots'),
  max: Ember.computed.max('pilots'),
  sum: Ember.computed.readOnly('sumPilots'),
});
