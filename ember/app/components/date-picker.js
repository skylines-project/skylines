import Component from '@ember/component';

import $ from 'jquery';

import isoDate from '../utils/iso-date';

export default Component.extend({
  tagName: 'span',

  date: null,
  onSelect() {},

  didInsertElement() {
    this._super(...arguments);
    let picker = $(this.element.querySelector('span')).datepicker({
      weekStart: 1,
    });

    this.set('picker', picker);

    picker.on('changeDate', e => {
      picker.data('datepicker').hide();
      this.onSelect(isoDate(e.date));
    });
  },

  willDestroyElement() {
    this._super(...arguments);
    let picker = this.picker;
    if (picker) {
      picker.off('changeDate');
    }

    this.set('picker', null);
  },
});
