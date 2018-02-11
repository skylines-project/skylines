import { computed } from '@ember/object';
import Component from '@ember/component';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  tagName: 'tr',
  classNames: ['small', 'selectable'],
  classNameBindings: ['selected'],

  inf: Infinity,

  leg: null,
  selection: null,
  onSelect() {},

  speed: computed('leg.{duration,distance}', function() {
    let duration = this.get('leg.duration');
    if (duration > 0) {
      return this.get('leg.distance') / duration;
    } else {
      return 0;
    }
  }),

  climbPercentage: computed('leg.{duration,climbDuration}', function() {
    let duration = this.get('leg.duration');
    if (duration > 0) {
      return this.get('leg.climbDuration') / duration;
    } else {
      return 0;
    }
  }),

  climbRate: computed('leg.{climbDuration,climbHeight}', function() {
    let duration = this.get('leg.climbDuration');
    if (duration > 0) {
      return this.get('leg.climbHeight') / duration;
    }
  }),

  glideRate: computed('leg.{cruiseDistance,cruiseHeight}', function() {
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
    let onSelect = this.get('onSelect');

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
