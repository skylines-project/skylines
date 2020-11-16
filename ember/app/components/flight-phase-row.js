import { action } from '@ember/object';
import { equal } from '@ember/object/computed';
import Component from '@glimmer/component';

import safeComputed from '../computed/safe-computed';

export default class extends Component {
  @equal('args.phase.type', 'circling') isCircling;
  @equal('args.phase.type', 'powered') isPowered;

  @equal('args.phase.circlingDirection', 'left') isCirclingLeft;
  @equal('args.phase.circlingDirection', 'right') isCirclingRight;

  @safeComputed('args.phase.glideRate', gr => (Math.abs(gr) > 1000 ? Infinity : gr)) glideRate;

  @safeComputed('args.selection', function (selection) {
    let phase = this.args.phase;
    return selection.start === phase.secondsOfDay && selection.end === phase.secondsOfDay + phase.duration;
  })
  selected;

  @action
  handleClick() {
    let onSelect = this.args.onSelect;

    if (this.selected) {
      onSelect(null);
    } else {
      let phase = this.args.phase;
      onSelect({
        start: phase.secondsOfDay,
        end: phase.secondsOfDay + phase.duration,
      });
    }
  }
}
