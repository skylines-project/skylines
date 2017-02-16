import Ember from 'ember';

import isoDate from '../utils/iso-date';

export default Ember.Component.extend({
  tagName: 'span',

  date: null,
  onSelect: null,

  didInsertElement() {
    let picker = this.$('span').datepicker({
      weekStart: 1,
    });

    this.set('picker', picker);

    picker.on('changeDate', e => {
      picker.data('datepicker').hide();
      this.getWithDefault('onSelect', Ember.K)(isoDate(e.date));
    });
  },

  willDestroyElement() {
    let picker = this.get('picker');
    if (picker) {
      picker.off('changeDate');
    }

    this.set('picker', null);
  },
});
