import { computed, get } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
  account: service(),

  tagName: '',

  clubMembers: null,
  pilotId: null,

  pilots: computed('account.{user,club}', 'clubMembers.[]', function() {
    let user = this.get('account.user');
    let club = this.get('account.club');
    let clubMembers = this.get('clubMembers');

    let pilots = [{ id: null }, user];
    if (club && clubMembers) {
      pilots.push({ groupName: get(club, 'name'), options: clubMembers });
    }

    return pilots;
  }),

  pilot: computed('pilotsWithNull.[]', 'pilotId', function() {
    return this.findPilot(this.get('pilotId') || null);
  }),

  actions: {
    onChange(pilot) {
      this.get('onChange')(pilot.id);
    },
  },

  findPilot(id) {
    let pilots = this.get('pilots');

    let pilot = pilots.findBy('id', id);
    if (pilot) {
      return pilot;
    }

    let clubMembers = pilots.get('lastObject.options');
    if (clubMembers) {
      return clubMembers.findBy('id', id);
    }
  },
});
