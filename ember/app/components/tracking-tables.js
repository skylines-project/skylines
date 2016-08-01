import Ember from 'ember';

export default Ember.Component.extend({
  account: Ember.inject.service(),

  tagName: '',

  tracks: null,
  friends: null,

  friendsTracks: Ember.computed('tracks.[]', 'friends.[]', 'account.user.id', function() {
    let self = this.get('account.user.id');
    if (Ember.isNone(self)) {
      return [];
    }

    let friends = this.get('friends');

    return this.get('tracks')
      .filter(track => (track.pilot.id === self || friends.contains(track.pilot.id)));
  }),

  othersTracks: Ember.computed.setDiff('tracks', 'friendsTracks'),
});
