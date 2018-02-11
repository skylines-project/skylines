import { alias } from '@ember/object/computed';
import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { task } from 'ember-concurrency';
import { or, eq, not } from 'ember-awesome-macros';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  account: service(),
  ajax: service(),

  flight: null,
  transitionTo() {},

  pilotName: or('flight.pilot.name', 'flight.pilotName'),
  copilotName: or('flight.copilot.name', 'flight.copilotName'),

  duration: safeComputed('flight.takeoffTime', 'flight.landingTime',
    (takeoff, landing) => (new Date(landing).getTime() - new Date(takeoff).getTime()) / 1000),

  registration: alias('flight.registration'),
  competitionId: alias('flight.competitionId'),

  isPilot: safeComputed('flight.pilot.id', 'flight.copilot.id', 'account.user.id',
    (pilotId, copilotId, accountId) => pilotId === accountId || copilotId === accountId),
  isOwner: safeComputed('flight.igcFile.owner.id', 'account.user.id',
    (ownerId, accountId) => ownerId === accountId),

  isWritable: or('isPilot', 'isOwner'),

  isPublic: eq('flight.privacyLevel', 0),
  isPrivate: not('isPublic'),

  deleteTask: task(function * () {
    let id = this.get('flight.id');
    yield this.get('ajax').request(`/api/flights/${id}/`, { method: 'DELETE' });
    this.set('showDeleteModal', false);
    this.get('transitionTo')('flights');
  }).drop(),

  publishTask: task(function * () {
    let id = this.get('flight.id');
    yield this.get('ajax').request(`/api/flights/${id}/`, { method: 'POST', json: { privacyLevel: 0 } });
    this.set('flight.privacyLevel', 0);
    this.set('showPublishModal', false);
  }).drop(),
});
