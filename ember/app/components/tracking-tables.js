import { computed } from '@ember/object';
import { setDiff } from '@ember/object/computed';
import { inject as service } from '@ember/service';
import { isNone } from '@ember/utils';
import Component from '@glimmer/component';

export default class TrackingTables extends Component {
  @service account;

  tracks = null;
  friends = null;

  @computed('args.{tracks.[],friends.[]}', 'account.user.id')
  get friendsTracks() {
    let self = this.account.user?.id;
    if (isNone(self)) {
      return [];
    }

    let friends = this.args.friends;

    return this.args.tracks.filter(track => track.pilot.id === self || friends.includes(track.pilot.id));
  }

  @setDiff('args.tracks', 'friendsTracks') othersTracks;
}
