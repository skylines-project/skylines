import { computed } from '@ember/object';

import Base from './-base';

export default Base.extend({
  translationKey: computed('accountUserIsActor', function() {
    let i = this.accountUserIsActor ? 2 : 1;
    return `timeline-events.club-join.message${i}`;
  }),
});
