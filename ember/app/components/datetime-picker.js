import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ['input-group', 'input-group-sm', 'date'],

  date: null,
  minDate: false,
  maxDate: false,
  onChange: Ember.K,

  didInsertElement() {
    this.$().datetimepicker({
      pickDate: false,
      useSeconds: true,
      format: 'HH:mm:ss',
      icons: {
        time: 'fa fa-clock-o',
        date: 'fa fa-calendar',
        up: 'fa fa-chevron-up',
        down: 'fa fa-chevron-down',
      },
      minDate: this.get('minDate'),
      maxDate: this.get('maxDate'),
    });

    this.$().on('dp.change', ({ date }) => {
      this.get('onChange')(date.toDate());
    });

    this.set('picker', this.$().data('DateTimePicker'));

    Ember.run.once(this, 'updateDate');
  },

  didUpdateAttrs() {
    Ember.run.once(this, 'updateDate');
  },

  willDestroyElement() {
    this.$().off('dp.change');
    this.set('picker', null);
  },

  updateDate() {
    let picker = this.get('picker');
    if (picker) {
      picker.setValue(this.get('date'));
    }
  },
});
