import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'tr',
  classNames: ['selectable'],

  flight: Ember.computed.alias('nearFlight.flight'),
  igcFile: Ember.computed.alias('flight.igc_file'),
  pilot: Ember.computed.alias('flight.pilot'),
  copilot: Ember.computed.alias('flight.co_pilot'),
  times: Ember.computed.alias('nearFlight.times'),

  colorStripeStyle: Ember.computed('nearFlight.color', function() {
    let color = this.get('nearFlight.color');
    if (color) {
      return Ember.String.htmlSafe(`background-color: ${color}`);
    }
  }),

  didInsertElement() {
    let popover_template = '<div class="popover" style="white-space: nowrap; z-index: 5000;">' +
                             '<div class="arrow"></div>' +
                             '<h3 class="popover-title"></h3>' +
                             '<div class="popover-content"></div>' +
                           '</div>';

    this.$('.times-column').popover({
      html: true,
      container: '#fullscreen-content',
      title: 'Periods',
      placement: 'right',
      trigger: 'hover',
      content: this.$('.times-table').html(),
      template: popover_template,
    });

    this.$('[rel=tooltip]').tooltip();
  },
});
