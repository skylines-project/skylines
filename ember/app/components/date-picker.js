import Component from '@ember/component';
import { action } from '@ember/object';

import $ from 'jquery';

import isoDate from '../utils/iso-date';

export default class DatePicker extends Component {
  tagName = '';

  date = null;
  onSelect() {}

  @action setup(element) {
    let picker = $(element).datepicker({
      weekStart: 1,
    });

    this.set('picker', picker);

    picker.on('changeDate', e => {
      picker.data('datepicker').hide();
      this.onSelect(isoDate(e.date));
    });
  }

  @action teardown() {
    let picker = this.picker;
    if (picker) {
      picker.off('changeDate');
    }

    this.set('picker', null);
  }
}
