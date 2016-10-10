import Ember from 'ember';

export default Ember.Component.extend({
  account: Ember.inject.service(),

  tagName: '',

  clubMembers: [],
  pilotId: null,

  pilots: Ember.computed('account.user', 'account.club', 'clubMembers.[]', function() {
    let user = this.get('account.user');
    let club = this.get('account.club');
    let clubMembers = this.get('clubMembers');

    let pilots = [{ id: null }, user];
    if (club && clubMembers) {
      pilots.push({ groupName: Ember.get(club, 'name'), options: clubMembers });
    }

    return pilots;
  }),

  pilot: Ember.computed('pilotsWithNull.[]', 'pilotId', function() {
    return this.findPilot(this.get('pilotId') || null);
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
