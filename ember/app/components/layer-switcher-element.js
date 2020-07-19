import Component from '@ember/component';
import { computed } from '@ember/object';

export default class LayerSwitcherElement extends Component {
  tagName = '';

  highlighted = false;

  @computed('layer.name')
  get imagePath() {
    return `../../images/layers/${this.get('layer.name')}.png`;
  }

  @computed('layer.visible', 'highlighted')
  get dimmed() {
    return !this.get('layer.visible') && !this.highlighted;
  }
}
