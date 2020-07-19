import { action } from '@ember/object';
import Component from '@glimmer/component';

import screenfull from 'screenfull';

export default class FullscreenButton extends Component {
  @action toggle() {
    let element = this.args.fullscreenElement;
    screenfull.toggle(document.querySelector(element));
  }
}
