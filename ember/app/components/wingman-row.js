import Component from '@ember/component';
import { computed } from '@ember/object';
import { alias, or } from '@ember/object/computed';
import { htmlSafe } from '@ember/template';

export default class extends Component {
  tagName = '';

  @alias('nearFlight.flight') flight;
  @alias('flight.igcFile') igcFile;
  @alias('flight.pilot') pilot;
  @or('flight.{pilot.name,pilotName}') pilotName;
  @alias('flight.copilot') copilot;
  @or('flight.{copilot.name,copilotName}') copilotName;
  @alias('nearFlight.times') times;

  @computed('nearFlight.color')
  get colorStripeStyle() {
    return htmlSafe(`border-left: 3px solid ${this.nearFlight.color ?? 'transparent'}`);
  }
}
