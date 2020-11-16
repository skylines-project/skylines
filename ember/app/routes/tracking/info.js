import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class InfoRoute extends Route {
  @service account;
  @service ajax;

  model() {
    let userId = this.get('account.user.id');
    if (userId) {
      return this.ajax.request('/api/settings');
    }
  }
}
