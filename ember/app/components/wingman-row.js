import Component from '@ember/component';
import { computed } from '@ember/object';
import { alias, or } from '@ember/object/computed';
import { htmlSafe } from '@ember/template';

export default Component.extend({
  tagName: '',
  flight: alias('nearFlight.flight'),
  igcFile: alias('flight.igcFile'),
  pilot: alias('flight.pilot'),
  pilotName: or('flight.{pilot.name,pilotName}'),
  copilot: alias('flight.copilot'),
  copilotName: or('flight.{copilot.name,copilotName}'),
  times: alias('nearFlight.times'),

  colorStripeStyle: computed('nearFlight.color', function() {
    return htmlSafe(`background-color: ${this.nearFlight.color}`);
  }),
});
