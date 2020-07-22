import Component from '@ember/component';
import { computed } from '@ember/object';

export default class LayerSwitcherElement extends Component {
  tagName = '';

  highlighted = false;

  @computed('visible', 'highlighted')
  get dimmed() {
    return !this.visible && !this.highlighted;
  }
}
