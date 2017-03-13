import Ember from 'ember';

import safeComputed from '../computed/safe-computed';

export default Ember.Component.extend({
  tagName: 'tr',
  classNames: ['small', 'selectable'],
  classNameBindings: ['selected'],

  inf: Infinity,

  leg: null,
  selection: null,

  speed: Ember.computed('leg.{duration,distance}', function() {
    let duration = this.get('leg.duration');
    if (duration > 0) {
      return this.get('leg.distance') / duration;
    } else {
      return 0;
    }
  }),

  climbPercentage: Ember.computed('leg.{duration,climbDuration}', function() {
    let duration = this.get('leg.duration');
    if (duration > 0) {
      return this.get('leg.climbDuration') / duration;
    } else {
      return 0;
    }
  }),

  climbRate: Ember.computed('leg.{climbDuration,climbHeight}', function() {
    let duration = this.get('leg.climbDuration');
    if (duration > 0) {
      return this.get('leg.climbHeight') / duration;
    }
  }),

  glideRate: Ember.computed('leg.{cruiseDistance,cruiseHeight}', function() {
    let distance = this.get('leg.cruiseDistance');
    let height = this.get('leg.cruiseHeight');

    if (Math.abs(height) > 0 && distance && Math.abs(distance / height) < 1000) {
      return distance / -height;
    } else {
      return Infinity;
    }
  }),

  selected: safeComputed('selection', function(selection) {
    let leg = this.get('leg');
    return selection.start === leg.start && selection.end === leg.start + leg.duration;
  }),

  click() {
    let onSelect = this.getWithDefault('onSelect', Ember.K);

    if (this.get('selected')) {
      onSelect(null);
    } else {
      let leg = this.get('leg');
      onSelect({
        start: leg.start,
        end: leg.start + leg.duration,
      });
    }
  },
});
