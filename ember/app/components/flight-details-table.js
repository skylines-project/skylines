import Component from '@ember/component';
import { not, equal, or, alias } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

import config from 'skylines/config/environment';

import safeComputed from '../computed/safe-computed';

export default class FlightDetailsTable extends Component {
  tagName = '';

  @service account;
  @service ajax;
  @service router;

  flight = null;

  @or('flight.pilot.name', 'flight.pilotName')
  pilotName;

  @or('flight.copilot.name', 'flight.copilotName')
  copilotName;

  @safeComputed(
    'flight.takeoffTime',
    'flight.landingTime',
    (takeoff, landing) => (new Date(landing).getTime() - new Date(takeoff).getTime()) / 1000,
  )
  duration;

  @alias('flight.registration')
  registration;

  @alias('flight.competitionId')
  competitionId;

  @safeComputed(
    'flight.pilot.id',
    'flight.copilot.id',
    'account.user.id',
    (pilotId, copilotId, accountId) => pilotId === accountId || copilotId === accountId,
  )
  isPilot;

  @safeComputed('flight.igcFile.owner.id', 'account.user.id', (ownerId, accountId) => ownerId === accountId)
  isOwner;

  @or('isPilot', 'isOwner')
  isWritable;

  @equal('flight.privacyLevel', 0)
  isPublic;

  @not('isPublic')
  isPrivate;

  @safeComputed('flight.igcFile.weglideStatus', 'flight.igcFile.weglideData', (status, data) =>
    status >= 200 && status < 300 ? data?.[0]?.id : null,
  )
  weglideFlightId;

  @safeComputed('weglideFlightId', id => `${config.WeGlide.web}/flights/${id}`) weglideLink;

  @(task(function* () {
    let id = this.get('flight.id');
    yield this.ajax.request(`/api/flights/${id}/`, { method: 'DELETE' });
    this.set('showDeleteModal', false);
    this.router.transitionTo('flights');
  }).drop())
  deleteTask;

  @(task(function* () {
    let id = this.get('flight.id');
    yield this.ajax.request(`/api/flights/${id}/`, { method: 'POST', json: { privacyLevel: 0 } });
    this.set('flight.privacyLevel', 0);
    this.set('showPublishModal', false);
  }).drop())
  publishTask;
}
