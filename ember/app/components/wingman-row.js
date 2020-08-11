import { computed } from '@ember/object';
import { alias, or } from '@ember/object/computed';
import { htmlSafe } from '@ember/template';
import Component from '@glimmer/component';

export default class extends Component {
  @alias('args.nearFlight.flight') flight;
  @alias('flight.igcFile') igcFile;
  @alias('flight.pilot') pilot;
  @or('flight.{pilot.name,pilotName}') pilotName;
  @alias('flight.copilot') copilot;
  @or('flight.{copilot.name,copilotName}') copilotName;
  @alias('args.nearFlight.times') times;

  @computed('args.nearFlight.color')
  get colorStripeStyle() {
    return htmlSafe(`border-left: 3px solid ${this.args.nearFlight.color ?? 'transparent'}`);
  }
}
