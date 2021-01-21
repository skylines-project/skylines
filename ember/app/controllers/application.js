import Controller from '@ember/controller';
import { action } from '@ember/object';

export default class ApplicationController extends Controller {
  @action search(text) {
    this.transitionToRoute('search', {
      queryParams: { text },
    });
  }
}
