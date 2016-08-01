import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  flightPhase: Ember.inject.service(),

  tagName: 'tr',
  classNames: ['small', 'selectable'],
  classNameBindings: ['selected'],

  selected: safeComputed('flightPhase.selection', function(selection) {
    let leg = this.get('leg');
    return selection.start === leg.start && selection.end === leg.start + leg.duration.seconds;
  }),

  click() {
    if (this.get('selected')) {
      this.set('flightPhase.selection', null);
    } else {
      let leg = this.get('leg');
      this.set('flightPhase.selection', {
        start: leg.start,
        end: leg.start + leg.duration.seconds,
        duration: leg.duration.seconds,
      });
    }
  },
});
