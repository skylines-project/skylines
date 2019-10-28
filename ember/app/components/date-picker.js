import Component from '@ember/component';
import { action } from '@ember/object';

import $ from 'jquery';

import isoDate from '../utils/iso-date';

export default Component.extend({
  tagName: '',

  date: null,
  onSelect() {},

  setup: action(function(element) {
    let picker = $(element).datepicker({
      weekStart: 1,
    });

    this.set('picker', picker);

    picker.on('changeDate', e => {
      picker.data('datepicker').hide();
      this.onSelect(isoDate(e.date));
    });
  }),

  teardown: action(function() {
    let picker = this.picker;
    if (picker) {
      picker.off('changeDate');
    }

    this.set('picker', null);
  }),
});
