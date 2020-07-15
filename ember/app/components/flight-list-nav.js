import { getOwner } from '@ember/application';
import Component from '@ember/component';
import { action } from '@ember/object';
import { notEmpty } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import safeComputed from '../computed/safe-computed';
import addDays from '../utils/add-days';

export default class FlightListNav extends Component {
  tagName = '';

  @service account;
  @service pinnedFlights;

  @notEmpty('pinnedFlights.pinned') hasPinned;

  @safeComputed('date', date => addDays(date, -1)) prevDate;
  @safeComputed('date', date => addDays(date, 1)) nextDate;

  init() {
    super.init(...arguments);
    this.set('router', getOwner(this).lookup('router:main'));
  }

  @action
  dateSelected(date) {
    this.router.transitionTo('flights.date', date);
  }
}
