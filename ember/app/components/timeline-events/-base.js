import Ember from 'ember';

import safeComputed from '../../utils/safe-computed';

export default Ember.Component.extend({
  account: Ember.inject.service(),

  tagName: 'tr',

  event: null,

  accountUserIsActor: safeComputed('account.user', 'event.actor',
    (accountUser, actor) => (accountUser.id == actor.id)),
});
