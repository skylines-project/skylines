import { computed } from '@ember/object';

import Base from './-base';

export default Base.extend({
  translationKey: computed('accountUserIsActor', function() {
    let i = this.get('accountUserIsActor') ? 2 : 1;
    return `timeline-events.new-user.message${i}`;
  }),
});
