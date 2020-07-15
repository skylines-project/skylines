import Component from '@ember/component';
import { computed } from '@ember/object';

export default class LayerSwitcherElement extends Component {
  tagName = '';

  highlighted = false;

  @computed('layer.visible', 'highlighted')
  get imagePath() {
    let colorful = this.get('layer.visible') || this.highlighted;
    return `../../images/layers/${this.get('layer.name')}${colorful ? '.png' : '.bw.png'}`;
  }
}
