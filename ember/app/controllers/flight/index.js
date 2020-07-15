import Controller from '@ember/controller';
import { action } from '@ember/object';

export default class IndexController extends Controller {
  queryParams = ['baselayer', 'overlays'];
  baselayer = null;
  overlays = null;

  @action
  transitionTo(...args) {
    this.transitionToRoute(...args);
  }
}
