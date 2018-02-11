import { setDiff } from '@ember/object/computed';
import { isNone } from '@ember/utils';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
  account: service(),

  tagName: '',

  tracks: null,
  friends: null,

  friendsTracks: computed('tracks.[]', 'friends.[]', 'account.user.id', function() {
    let self = this.get('account.user.id');
    if (isNone(self)) {
      return [];
    }

    let friends = this.get('friends');

    return this.get('tracks')
      .filter(track => (track.pilot.id === self || friends.includes(track.pilot.id)));
  }),

  othersTracks: setDiff('tracks', 'friendsTracks'),
});
