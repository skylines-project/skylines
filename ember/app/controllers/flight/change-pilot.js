import Controller from '@ember/controller';
import { action } from '@ember/object';

export default class ChangePilotController extends Controller {
  @action
  transitionToFlight() {
    this.transitionToRoute('flight', this.get('model.id'));
  }
}
