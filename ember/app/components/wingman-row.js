import Ember from 'ember';
import { conditional, tag } from 'ember-awesome-macros';
import { htmlSafe } from 'ember-awesome-macros/string';

export default Ember.Component.extend({
  tagName: 'tr',
  classNames: ['selectable'],

  flight: Ember.computed.alias('nearFlight.flight'),
  igcFile: Ember.computed.alias('flight.igcFile'),
  pilot: Ember.computed.alias('flight.pilot'),
  pilotName: Ember.computed.or('flight.{pilot.name,pilotName}'),
  copilot: Ember.computed.alias('flight.copilot'),
  copilotName: Ember.computed.or('flight.{copilot.name,copilotName}'),
  times: Ember.computed.alias('nearFlight.times'),

  colorStripeStyle: conditional('nearFlight.color', htmlSafe(tag`background-color: ${'nearFlight.color'}`)),

  didInsertElement() {
    this.$('[rel=tooltip]').tooltip();
  },
});
