import Ember from 'ember';

import safeComputed from '../../utils/safe-computed';

export default Ember.Component.extend({
  account: Ember.inject.service(),

  tagName: 'tr',

  event: null,

  accountUserIsActor: safeComputed('account.user', 'event.actor',
    (accountUser, actor) => (accountUser.id == actor.id)),

  accountUserIsPilot: safeComputed('account.user', 'event.flight',
    (accountUser, flight) => (accountUser.id == flight.pilot_id || accountUser.id == flight.copilot_id)),

  translationKey: Ember.computed('accountUserIsActor', 'accountUserIsPilot', function() {
    let i = 1;
    if (this.get('accountUserIsActor')) { i += 1; }
    if (this.get('accountUserIsPilot')) { i += 2; }
    return `timeline-events.flight-comment.message${i}`;
  }),
});
