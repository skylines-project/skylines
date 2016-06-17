import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  tagName: 'tr',
  classNames: ['selectable'],

  flight: Ember.computed.alias('nearFlight.flight'),
  igcFile: Ember.computed.alias('flight.igc_file'),
  pilot: Ember.computed.alias('flight.pilot'),
  copilot: Ember.computed.alias('flight.co_pilot'),
  times: Ember.computed.alias('nearFlight.times'),

  colorStripeStyle: safeComputed('nearFlight.color',
    color => Ember.String.htmlSafe(`background-color: ${color}`)),

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
