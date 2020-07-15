import Component from '@ember/component';
import { computed } from '@ember/object';
import { setDiff } from '@ember/object/computed';
import { inject as service } from '@ember/service';
import { isNone } from '@ember/utils';

export default class TrackingTables extends Component {
  tagName = '';

  @service account;

  tracks = null;
  friends = null;

  @computed('tracks.[]', 'friends.[]', 'account.user.id')
  get friendsTracks() {
    let self = this.get('account.user.id');
    if (isNone(self)) {
      return [];
    }

    let friends = this.friends;

    return this.tracks.filter(track => track.pilot.id === self || friends.includes(track.pilot.id));
  }

  @setDiff('tracks', 'friendsTracks') othersTracks;
}
