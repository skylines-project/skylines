import { action } from '@ember/object';
import { notEmpty } from '@ember/object/computed';
import { inject as service } from '@ember/service';
import Component from '@glimmer/component';

import safeComputed from '../computed/safe-computed';
import addDays from '../utils/add-days';

export default class FlightListNav extends Component {
  @service account;
  @service pinnedFlights;
  @service router;

  @notEmpty('pinnedFlights.pinned') hasPinned;

  @safeComputed('args.date', date => addDays(date, -1)) prevDate;
  @safeComputed('args.date', date => addDays(date, 1)) nextDate;

  @action
  dateSelected(_, date) {
    this.router.transitionTo('flights.date', date);
  }

  @action
  openDatePicker(event) {
    event.preventDefault();
    event.stopPropagation();
    this.flatpickr.open();
  }

  @action
  closeDatePicker() {
    this.flatpickr.close();
  }

  @action
  maybePreventDefault(event) {
    // if the click happened inside the datepicker we don't want the link to trigger
    let { target } = event;

    for (let parent of parents(target)) {
      if (parent.classList.contains('flatpickr-wrapper')) {
        event.preventDefault();
        event.stopPropagation();
        return;
      }
    }
  }
}

function* parents(element) {
  let parent = element;
  while ((parent = parent.parentElement)) {
    yield parent;
  }
}
