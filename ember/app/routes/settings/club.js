import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class ClubRoute extends Route {
  @service ajax;

  model() {
    return this.ajax.request('/api/clubs');
  }
}
