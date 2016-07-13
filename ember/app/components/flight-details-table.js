import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  account: Ember.inject.service(),

  flight: null,

  pilotName: Ember.computed.or('flight.pilot.name', 'flight.pilotName'),
  copilotName: Ember.computed.or('flight.copilot.name', 'flight.copilotName'),

  duration: safeComputed('flight.takeoffTime', 'flight.landingTime',
    (takeoff, landing) => (new Date(landing).getTime() - new Date(takeoff).getTime()) / 1000),

  registration: Ember.computed.or('flight.registration', 'flight.igcFile.registration'),
  competitionId: Ember.computed.or('flight.competitionId', 'flight.igcFile.competitionId'),

  isPilot: safeComputed('flight.pilot.id', 'flight.copilot.id', 'account.user.id',
    (pilotId, copilotId, accountId) => pilotId === accountId || copilotId === accountId),
  isOwner: safeComputed('flight.igcFile.owner.id', 'account.user.id',
    (ownerId, accountId) => ownerId === accountId),

  isWritable: Ember.computed.or('isPilot', 'isOwner'),

  isPublic: Ember.computed.equal('flight.privacyLevel', 0),
  isPrivate: Ember.computed.not('isPublic'),
});
