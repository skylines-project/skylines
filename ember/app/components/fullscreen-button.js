/* global BigScreen */

import { action } from '@ember/object';

import Component from '@glimmer/component';

export default class FullscreenButton extends Component {
  @action toggle() {
    let element = this.args.fullscreenElement;
    BigScreen.toggle(document.querySelector(element));
  }
}
