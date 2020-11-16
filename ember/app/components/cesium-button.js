import { action } from '@ember/object';
import Component from '@glimmer/component';

export default class CesiumButton extends Component {
  @action toggle() {
    if (this.args.enabled) {
      this.args.onDisable();
    } else {
      this.args.onEnable();
    }
  }
}
