import { computed } from '@ember/object';

import Base from './-base';
import safeComputed from '../../computed/safe-computed';

export default Base.extend({
  accountUserIsFollowed: safeComputed('account.user', 'event.user',
    (accountUser, user) => (accountUser.id === user.id)),

  translationKey: computed('accountUserIsActor', 'accountUserIsFollowed', function() {
    let i = 1;
    if (this.get('accountUserIsActor')) { i += 1; }
    if (this.get('accountUserIsFollowed')) { i += 2; }
    return `timeline-events.follower.message${i}`;
  }),
});
