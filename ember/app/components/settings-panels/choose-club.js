import Ember from 'ember';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  classNames: ['panel', 'panel-default'],

  clubs: [],
  clubId: null,
  pending: false,
  messageKey: null,
  error: null,

  clubsWithNull: Ember.computed('clubs.[]', function() {
    return [{ id: null }].concat(this.get('clubs'));
  }),

  club: Ember.computed('clubId', {
    get() {
      return this.get('clubsWithNull').findBy('id', this.get('clubId'));
    },
    set(key, value) {
      this.set('clubId', value.id);
      return value;
    },
  }),

  sendChangeRequest() {
    let club = this.get('club');
    let json = { id: club.id };

    this.set('pending', true);
    this.get('ajax').request('/settings/club', { method: 'POST', json }).then(() => {
      this.setProperties({
        messageKey: 'club-has-been-changed',
        error: null,
      });

      this.get('account').set('club', (club.id === null) ? {} : club);
    }).catch(error => {
      this.setProperties({ messageKey: null, error });
    }).finally(() => {
      this.set('pending', false);
    });
  },

  actions: {
    submit() {
      this.sendChangeRequest();
    },
  },
});
