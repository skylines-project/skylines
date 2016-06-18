import Ember from 'ember';

export default Ember.Component.extend({
  tagName: '',

  tracks: null,
  friends: null,
  self: null,

  friendsTracks: Ember.computed('tracks.[]', 'friends.[]', 'self', function() {
    let self = this.get('self');
    if (Ember.isNone(self)) {
      return [];
    }

    let friends = this.get('friends');

    return this.get('tracks')
      .filter(track => (track.pilot.id === self || friends.contains(track.pilot.id)));
  }),

  othersTracks: Ember.computed.setDiff('tracks', 'friendsTracks'),
});
