import { alias, or } from '@ember/object/computed';
import Component from '@ember/component';
import { conditional, tag } from 'ember-awesome-macros';
import { htmlSafe } from 'ember-awesome-macros/string';

export default Component.extend({
  tagName: 'tr',
  classNames: ['selectable'],

  flight: alias('nearFlight.flight'),
  igcFile: alias('flight.igcFile'),
  pilot: alias('flight.pilot'),
  pilotName: or('flight.{pilot.name,pilotName}'),
  copilot: alias('flight.copilot'),
  copilotName: or('flight.{copilot.name,copilotName}'),
  times: alias('nearFlight.times'),

  colorStripeStyle: conditional('nearFlight.color', htmlSafe(tag`background-color: ${'nearFlight.color'}`)),
});
