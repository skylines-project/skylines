import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  flightPhase: Ember.inject.service(),

  tagName: 'tr',
  classNames: ['small', 'selectable'],
  classNameBindings: ['selected'],

  speed: Ember.computed('leg.duration', 'leg.distance', function() {
    let duration = this.get('leg.duration');
    if (duration > 0) {
      return this.get('leg.distance') / duration;
    } else {
      return 0;
    }
  }),

  climbPercentage: Ember.computed('leg.duration', 'leg.climbDuration', function() {
    let duration = this.get('leg.duration');
    if (duration > 0) {
      return this.get('leg.climbDuration') / duration;
    } else {
      return 0;
    }
  }),

  climbRate: Ember.computed('leg.climbDuration', 'leg.climbHeight', function() {
    let duration = this.get('leg.climbDuration');
    if (duration > 0) {
      return this.get('leg.climbHeight') / duration;
    }
  }),

  glideRate: Ember.computed('leg.cruiseDistance', 'leg.cruiseHeight', function() {
    let distance = this.get('leg.cruiseDistance');
    let height = this.get('leg.cruiseHeight');

    if (Math.abs(height) > 0 && distance && Math.abs(distance / height) < 1000) {
      return distance / -height;
    } else {
      return Infinity;
    }
  }),

  inf: Infinity,

  selected: safeComputed('flightPhase.selection', function(selection) {
    let leg = this.get('leg');
    return selection.start === leg.start && selection.end === leg.start + leg.duration;
  }),

  click() {
    if (this.get('selected')) {
      this.set('flightPhase.selection', null);
    } else {
      let leg = this.get('leg');
      this.set('flightPhase.selection', {
        start: leg.start,
        end: leg.start + leg.duration,
        duration: leg.duration,
      });
    }
  },
});
