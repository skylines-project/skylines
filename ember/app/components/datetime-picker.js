import Component from '@ember/component';
import { once } from '@ember/runloop';

import $ from 'jquery';

export default Component.extend({
  classNames: ['input-group', 'input-group-sm', 'date'],

  date: null,
  minDate: false,
  maxDate: false,
  onChange: null,

  didInsertElement() {
    this._super(...arguments);

    let $element = $(this.element);

    $element.datetimepicker({
      pickDate: false,
      useSeconds: true,
      format: 'HH:mm:ss',
      icons: {
        time: 'fa fa-clock-o',
        date: 'fa fa-calendar',
        up: 'fa fa-chevron-up',
        down: 'fa fa-chevron-down',
      },
      minDate: this.minDate,
      maxDate: this.maxDate,
    });

    $element.on('dp.change', ({ date }) => {
      this.onChange(date.toDate());
    });

    this.set('picker', $element.data('DateTimePicker'));

    once(this, 'updateDate');
  },

  didUpdateAttrs() {
    this._super(...arguments);
    once(this, 'updateDate');
  },

  willDestroyElement() {
    this._super(...arguments);
    $(this.element).off('dp.change');
    this.set('picker', null);
  },

  updateDate() {
    let picker = this.picker;
    if (picker) {
      picker.setValue(this.date);
    }
  },
});
