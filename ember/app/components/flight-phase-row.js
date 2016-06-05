import Ember from 'ember';

export default Ember.Component.extend({
  flightPhase: Ember.inject.service(),

  tagName: 'tr',
  classNameBindings: ['selected'],
  attributeBindings: ['style'],

  selected: Ember.computed('flightPhase.selection', function() {
    let selection = this.get('flightPhase.selection');
    if (selection) {
      let phase = this.get('phase');
      return selection.start === phase.start.seconds && selection.end === phase.start.seconds + phase.duration.seconds;
    }
  }),

  click() {
    if (this.get('selected')) {
      this.set('flightPhase.selection', null);
    } else {
      let phase = this.get('phase');
      this.set('flightPhase.selection', {
        start: phase.start.seconds,
        end: phase.start.seconds + phase.duration.seconds,
        duration: phase.duration.seconds
      });
    }
  },
});
