import Ember from 'ember';

export default Ember.Component.extend({
  flightPhase: Ember.inject.service(),

  tagName: 'tr',
  classNames: ['small'],
  classNameBindings: ['selected'],
  attributeBindings: ['style'],

  style: Ember.computed(function() {
    return Ember.String.htmlSafe('cursor: pointer');
  }),

  selected: Ember.computed('flightPhase.selection', function() {
    let selection = this.get('flightPhase.selection');
    if (selection) {
      let leg = this.get('leg');
      return selection.start === leg.start && selection.end === leg.start + leg.duration.seconds;
    }
  }),

  click() {
    if (this.get('selected')) {
      this.set('flightPhase.selection', null);
    } else {
      let leg = this.get('leg');
      this.set('flightPhase.selection', {
        start: leg.start,
        end: leg.start + leg.duration.seconds,
        duration: leg.duration.seconds
      });
    }
  },
});
