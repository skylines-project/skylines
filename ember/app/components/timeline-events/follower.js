import { computed } from '@ember/object';

import safeComputed from '../../computed/safe-computed';
import Base from './-base';

export default Base.extend({
  accountUserIsFollowed: safeComputed('account.user', 'event.user', (accountUser, user) => accountUser.id === user.id),

  translationKey: computed('accountUserIsActor', 'accountUserIsFollowed', function() {
    let i = 1;
    if (this.accountUserIsActor) {
      i += 1;
    }
    if (this.accountUserIsFollowed) {
      i += 2;
    }
    return `timeline-events.follower.message${i}`;
  }),
});
