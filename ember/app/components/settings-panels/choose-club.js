import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default Component.extend({
  ajax: service(),
  account: service(),

  classNames: ['panel', 'panel-default'],

  clubs: null,
  clubId: null,
  messageKey: null,
  error: null,

//  clubsWithNull: computed('clubs.[]', function() {
//    return [{ id: null }].concat(this.clubs);
//  }),

//  club: for the current value in selector
  club: computed('clubId', {
//    get() {
//      return this.clubsWithNull.findBy('id', this.clubId || null);
//    },
    set(key, value) {
      this.set('clubId', value.id);
      return value;
    },
  }),


  saveTask: task(function*() {
    console.log('test1bch');
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
  }).drop(),
});
