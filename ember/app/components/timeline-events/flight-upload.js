import Ember from 'ember';

import Base from './-base';

export default Base.extend({
  translationKey: Ember.computed('accountUserIsActor', function() {
    let i = this.get('accountUserIsActor') ? 2 : 1;
    return `timeline-events.flight-upload.message${i}`;
  }),
});
