import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  flightPhase: Ember.inject.service(),

  tagName: 'tr',
  classNames: ['selectable'],
  classNameBindings: ['selected'],

  selected: safeComputed('flightPhase.selection', function(selection) {
    let phase = this.get('phase');
    return selection.start === phase.secondsOfDay && selection.end === phase.secondsOfDay + phase.duration;
  }),

  click() {
    if (this.get('selected')) {
      this.set('flightPhase.selection', null);
    } else {
      let phase = this.get('phase');
      this.set('flightPhase.selection', {
        start: phase.secondsOfDay,
        end: phase.secondsOfDay + phase.duration,
        duration: phase.duration,
      });
    }
  },
});
