import Ember from 'ember';

export default Ember.Component.extend({
  account: Ember.inject.service(),

  tagName: '',

  clubMembers: [],
  pilotId: null,

  pilots: Ember.computed('account.user', 'account.club', 'clubMembers.[]', function() {
    let pilots = [{ id: null }, this.get('account.user')];
    if (this.get('account.club')) {
      pilots.push({ groupName: this.get('account.club.name'), options: this.get('clubMembers') });
    }
    return pilots;
  }),

  pilot: Ember.computed('pilotsWithNull.[]', 'pilotId', function() {
    return this.findPilot(this.get('pilotId'));
  }),

  findPilot(id) {
    let pilots = this.get('pilots');

    let pilot = pilots.findBy('id', id);
    if (pilot) return pilot;

    let clubMembers = pilots.get('lastObject.options');
    if (clubMembers) {
      return clubMembers.findBy('id', id);
    }
  },

  actions: {
    onChange(pilot) {
      this.get('onChange')(pilot.id);
    },
  },
});
