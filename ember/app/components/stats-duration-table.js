import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-condensed', 'table-striped'],

  years: null,

  durations: Ember.computed.mapBy('years', 'duration'),
  max: Ember.computed.max('durations'),
  sum: Ember.computed.sum('durations'),
});
