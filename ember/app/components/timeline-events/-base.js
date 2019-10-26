import Component from '@ember/component';
import { inject as service } from '@ember/service';

import safeComputed from '../../computed/safe-computed';

export default Component.extend({
  account: service(),

  tagName: '',

  event: null,

  accountUserIsActor: safeComputed('account.user', 'event.actor', (accountUser, actor) => accountUser.id === actor.id),
});
