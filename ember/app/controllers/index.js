import Controller from '@ember/controller';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default class IndexController extends Controller {
  @service account;

  @computed('account.user')
  get notificationsTarget() {
    return this.account.user ? 'notifications' : 'timeline';
  }
}
