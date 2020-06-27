import Component from '@ember/component';
import { action } from '@ember/object';
import { equal } from '@ember/object/computed';

import safeComputed from '../computed/safe-computed';

export default class extends Component {
  tagName = '';

  @equal('phase.type', 'circling') isCircling;
  @equal('phase.type', 'powered') isPowered;

  @equal('phase.circlingDirection', 'left') isCirclingLeft;
  @equal('phase.circlingDirection', 'right') isCirclingRight;

  @safeComputed('phase.glideRate', gr => (Math.abs(gr) > 1000 ? Infinity : gr)) glideRate;

  @safeComputed('selection', function (selection) {
    let phase = this.phase;
    return selection.start === phase.secondsOfDay && selection.end === phase.secondsOfDay + phase.duration;
  })
  selected;

  @action
  handleClick() {
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
  }
}
