import { computed } from '@ember/object';
import Component from '@glimmer/component';

export default class LayerSwitcherElement extends Component {
  highlighted = false;

  @computed('args.visible', 'highlighted')
  get dimmed() {
    return !this.args.visible && !this.highlighted;
  }
}
