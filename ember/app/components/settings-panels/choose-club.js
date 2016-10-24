import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  classNames: ['panel', 'panel-default'],

  clubs: [],
  clubId: null,
  messageKey: null,
  error: null,

  clubsWithNull: Ember.computed('clubs.[]', function() {
    return [{ id: null }].concat(this.get('clubs'));
  }),

  club: Ember.computed('clubId', {
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
    let json = { clubId: club.id };

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
