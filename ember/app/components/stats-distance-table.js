import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,

  distances: Ember.computed.mapBy('years', 'distance'),
  max: Ember.computed.max('distances'),
  sum: Ember.computed.sum('distances'),
});
