import Ember from 'ember';

import safeComputed from '../computed/safe-computed';

export default Ember.Component.extend({
  flightPhase: Ember.inject.service(),

  tagName: 'tr',
  classNames: ['selectable'],
  classNameBindings: ['selected'],

  isCircling: Ember.computed.equal('phase.type', 'circling'),
  isPowered: Ember.computed.equal('phase.type', 'powered'),

  isCirclingLeft: Ember.computed.equal('phase.circlingDirection', 'left'),
  isCirclingRight: Ember.computed.equal('phase.circlingDirection', 'right'),

  glideRate: safeComputed('phase.glideRate', gr => ((Math.abs(gr) > 1000) ? Infinity : gr)),

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
      });
    }
  },
});
