import Component from '@ember/component';
import { or, equal, not } from '@ember/object/computed';

export default Component.extend({
  tagName: '',
  flight: null,

  pilotName: or('flight.pilot.name', 'flight.pilotName'),
  copilotName: or('flight.copilot.name', 'flight.copilotName'),

  isPublic: equal('flight.privacyLevel', 0),
  isPrivate: not('isPublic'),
});
