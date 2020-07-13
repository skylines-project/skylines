import { or, equal, not } from '@ember/object/computed';

import Component from '@glimmer/component';

export default class FlightListRow extends Component {
  @or('args.flight.pilot.name', 'args.flight.pilotName') pilotName;
  @or('args.flight.copilot.name', 'args.flight.copilotName') copilotName;

  @equal('args.flight.privacyLevel', 0) isPublic;
  @not('isPublic') isPrivate;
}
