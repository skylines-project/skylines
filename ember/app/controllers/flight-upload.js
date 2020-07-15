import Controller from '@ember/controller';
import { action } from '@ember/object';

export default class FlightUploadController extends Controller {
  @action
  transitionTo(...args) {
    this.transitionToRoute(...args);
  }
}
