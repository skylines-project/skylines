import Component from '@ember/component';
import { action } from '@ember/object';

export default class CesiumButton extends Component {
  tagName = '';

  @action toggle() {
    if (this.enabled) {
      this.onDisable();
    } else {
      this.onEnable();
    }
  }
}
