import Component from '@ember/component';
import { equal } from '@ember/object/computed';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  tagName: 'tr',
  classNames: ['selectable'],
  classNameBindings: ['selected'],

  phase: null,
  selection: null,
  onSelect() {},

  isCircling: equal('phase.type', 'circling'),
  isPowered: equal('phase.type', 'powered'),

  isCirclingLeft: equal('phase.circlingDirection', 'left'),
  isCirclingRight: equal('phase.circlingDirection', 'right'),

  glideRate: safeComputed('phase.glideRate', gr => (Math.abs(gr) > 1000 ? Infinity : gr)),

  selected: safeComputed('selection', function(selection) {
    let phase = this.phase;
    return selection.start === phase.secondsOfDay && selection.end === phase.secondsOfDay + phase.duration;
  }),

  click() {
    let onSelect = this.onSelect;

    if (this.selected) {
      onSelect(null);
    } else {
      let phase = this.phase;
      onSelect({
        start: phase.secondsOfDay,
        end: phase.secondsOfDay + phase.duration,
      });
    }
  },
});
