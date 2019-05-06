import Component from '@ember/component';
import { computed } from '@ember/object';
import { setDiff } from '@ember/object/computed';
import { inject as service } from '@ember/service';
import { isNone } from '@ember/utils';

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

    let friends = this.friends;

    return this.tracks.filter(track => track.pilot.id === self || friends.includes(track.pilot.id));
  }),

  othersTracks: setDiff('tracks', 'friendsTracks'),
});
