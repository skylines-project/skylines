import Component from '@ember/component';
import { action } from '@ember/object';
import { once } from '@ember/runloop';

import $ from 'jquery';

export default Component.extend({
  tagName: '',

  date: null,
  minDate: false,
  maxDate: false,
  onChange: null,

  setup: action(function(element) {
    let $element = $(element);

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
  }),

  didUpdateAttrs() {
    this._super(...arguments);
    once(this, 'updateDate');
  },

  teardown: action(function(element) {
    $(element).off('dp.change');
    this.set('picker', null);
  }),

  updateDate() {
    let picker = this.picker;
    if (picker) {
      picker.setValue(this.date);
    }
  },
});
