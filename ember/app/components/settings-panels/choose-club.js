import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { task } from 'ember-concurrency';

export default Component.extend({
  ajax: service(),
  account: service(),

  classNames: ['panel', 'panel-default'],

  clubs: null,
  clubId: null,
  messageKey: null,
  error: null,

  clubsWithNull: computed('clubs.[]', function() {
    return [{ id: null }].concat(this.get('clubs'));
  }),

  club: computed('clubId', {
    get() {
      return this.get('clubsWithNull').findBy('id', this.get('clubId') || null);
    },
    set(key, value) {
      this.set('clubId', value.id);
      return value;
    },
  }),

  saveTask: task(function * () {
    let club = this.get('club');
    let json = { clubId: club ? club.id : null };

    try {
      yield this.get('ajax').request('/api/settings/', { method: 'POST', json });
      this.setProperties({
        messageKey: 'club-has-been-changed',
        error: null,
      });

      this.get('account').set('club', (club.id === null) ? {} : club);
    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});
