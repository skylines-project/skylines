import { computed } from '@ember/object';

import safeComputed from '../../computed/safe-computed';
import Base from './-base';

export default Base.extend({
  accountUserIsPilot: safeComputed(
    'account.user',
    'event.flight',
    (accountUser, flight) => accountUser.id === flight.pilot_id || accountUser.id === flight.copilot_id,
  ),

  translationKey: computed('accountUserIsActor', 'accountUserIsPilot', function() {
    let i = 1;
    if (this.accountUserIsActor) {
      i += 1;
    }
    if (this.accountUserIsPilot) {
      i += 2;
    }
    return `timeline-events.flight-comment.message${i}`;
  }),
});
