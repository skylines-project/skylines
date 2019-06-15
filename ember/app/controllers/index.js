import Controller from '@ember/controller';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Controller.extend({
  account: service(),

  notificationsTarget: computed('account.user', function() {
    return this.account.user ? 'notifications' : 'timeline';
  }),
});
