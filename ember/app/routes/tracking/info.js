import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
  account: service(),
  ajax: service(),

  model() {
    let userId = this.get('account.user.id');
    if (userId) {
      return this.ajax.request('/api/settings');
    }
  },
});
