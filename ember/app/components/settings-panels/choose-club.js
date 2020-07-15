import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default class ChooseClub extends Component {
  tagName = '';

  @service ajax;
  @service account;

  clubs = null;
  clubId = null;
  messageKey = null;
  error = null;

  @computed('clubs.[]')
  get clubsWithNull() {
    return [{ id: null }].concat(this.clubs);
  }

  @computed('clubId')
  get club() {
    return this.clubsWithNull.findBy('id', this.clubId || null);
  }

  set club(value) {
    this.set('clubId', value.id);
    return value;
  }

  @(task(function* () {
    let club = this.club;
    let json = { clubId: club ? club.id : null };

    try {
      yield this.ajax.request('/api/settings/', { method: 'POST', json });
      this.setProperties({
        messageKey: 'club-has-been-changed',
        error: null,
      });

      this.account.set('club', club.id === null ? {} : club);
    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop())
  saveTask;
}
